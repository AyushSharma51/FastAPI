"""
conftest.py — Shared pytest fixtures for the entire test suite.

pytest automatically discovers and loads this file before running any tests.
Every fixture defined here is available to ALL test files in the same directory
and all subdirectories — no import needed in the test files.

Why in-memory SQLite?
  - Tests never touch the real matches.db file on disk
  - Each test run starts with a clean, empty schema
  - SQLite in-memory is fast — no file I/O
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from datetime import date
from src.app.database import get_db
from src.app.db_models import Base
from src.app.db_models import League as LeagueModel
from src.app.db_models import Season
from src.app.main import app

# ---------------------------------------------------------------------------
# Database URL
# ---------------------------------------------------------------------------

# "sqlite:///:memory:" means the database lives entirely in RAM.
# It is created when the engine connects and destroyed when the process exits.
# Nothing is written to disk, so tests can never corrupt your real data.
TEST_DATABASE_URL = "sqlite:///:memory:"


# ---------------------------------------------------------------------------
# Engine fixture  (scope="session")
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def engine():
    """
    Creates the SQLAlchemy engine and builds the schema ONCE per test session.

    scope="session" means pytest creates this fixture a single time and shares
    it across every test in the entire run. This is efficient because creating
    tables is slow and there is no reason to redo it for every test.

    What happens here step by step:
      1. create_engine() sets up the connection factory for in-memory SQLite.
         check_same_thread=False is required by SQLite when the same connection
         is used across multiple threads (FastAPI's TestClient does this).
      2. Base.metadata.create_all() reads every ORM model class that inherits
         from Base (League, Season, Team, etc.) and issues the corresponding
         CREATE TABLE statements against the in-memory DB.
      3. yield hands the engine to whoever requested this fixture.
      4. After all tests finish, drop_all() issues DROP TABLE for every table
         and dispose() closes all open connections in the connection pool.
    """
    _engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )

    # Mirror the same constraint enforcement as production
    @event.listens_for(_engine, "connect")
    def enable_fk(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(_engine)  # CREATE TABLE for every ORM model
    yield _engine
    Base.metadata.drop_all(_engine)  # DROP TABLE after the session ends
    _engine.dispose()  # close all pooled connections


# ---------------------------------------------------------------------------
# DB session fixture  (scope="function"  <- the default)
# ---------------------------------------------------------------------------


@pytest.fixture()
def db_session(engine):
    """
    Gives each test its own isolated database session using the
    SAVEPOINT / rollback trick — without recreating the schema each time.

    Why not just create a fresh engine per test?
      Creating tables is slow. Instead we reuse the same schema and undo
      every INSERT/UPDATE/DELETE by rolling back after each test.

    How the savepoint trick works:
      1. connection = engine.connect()
            Opens a real DBAPI connection from the engine's pool.

      2. transaction = connection.begin()
            Starts an outer transaction. Nothing is committed to the DB
            until this transaction is committed — and we never commit it.

      3. session = Session(bind=connection)
            Creates an ORM session bound to this specific connection.
            When the service code inside a test calls session.commit(),
            SQLAlchemy actually issues a SAVEPOINT (a nested transaction)
            rather than a real COMMIT, because the outer transaction is
            still open. This means the data appears committed to the code
            being tested, but can still be fully rolled back afterward.

      4. yield session
            The test runs here. Any rows added, updated, or deleted exist
            only within the outer transaction.

      5. session.close()  ->  transaction.rollback()  ->  connection.close()
            After the test finishes, we close the session, roll back the
            outer transaction (undoing every change made during the test),
            and return the connection to the pool. The next test starts
            with a perfectly clean database.

    Result: tests are fully isolated from each other with no performance cost.
    """
    connection = engine.connect()
    transaction = connection.begin()  # open outer transaction
    session = Session(bind=connection)  # ORM session on that connection

    yield session  # test runs here

    session.close()
    transaction.rollback()  # undo everything the test did
    connection.close()


# ---------------------------------------------------------------------------
# FastAPI test client fixture
# ---------------------------------------------------------------------------


@pytest.fixture()
def client(db_session):
    """
    Provides an HTTP test client wired to the same rolled-back DB session.

    The problem this solves:
      FastAPI's get_db dependency normally creates its own Session from the
      real engine (the one pointing at matches.db). If we don't override it,
      our test HTTP calls would hit the real database and our rollback trick
      would not work — the route handler's session would be a different
      object than db_session.

    How dependency_overrides works:
      FastAPI keeps a dict called dependency_overrides. When a route declares
      Depends(get_db), FastAPI checks this dict first. If get_db is a key,
      it calls the override function instead. Here we replace get_db with a
      function that yields the same db_session fixture — so the route handler,
      the service, and the test are all sharing one connection and one
      transaction. The rollback in db_session therefore undoes HTTP-triggered
      changes too.

    TestClient(app) as c:
      Uses httpx under the hood to make real HTTP requests to the FastAPI app
      in-process (no network involved). The `with` block ensures the app's
      startup and shutdown events (lifespan) fire correctly.

    app.dependency_overrides.clear():
      Removes the override after the test so it does not leak into other tests.
    """

    def _override_get_db():
        yield db_session  # give the route handler our test session

    app.dependency_overrides[get_db] = _override_get_db

    with TestClient(app) as c:
        yield c  # test makes HTTP calls here

    app.dependency_overrides.clear()  # clean up after the test


# ---------------------------------------------------------------------------
# Convenience data fixtures
# ---------------------------------------------------------------------------
# These fixtures pre-populate the database with rows that tests commonly need.
# Because db_session rolls back after every test, each fixture's data exists
# only for the duration of the test that requested it.
# ---------------------------------------------------------------------------


@pytest.fixture()
def league_in_db(db_session) -> LeagueModel:
    """
    Inserts one active (not deleted) League row and returns the ORM object.

    Tests that need an existing league to work with (e.g. update, delete,
    or get tests) use this instead of repeating the insert themselves.
    """
    league = LeagueModel(name="Premier League")
    db_session.add(league)
    db_session.commit()  # issues a SAVEPOINT internally (see db_session)
    db_session.refresh(league)  # loads the auto-generated id back onto the object
    return league


@pytest.fixture()
def soft_deleted_league(db_session) -> LeagueModel:
    """
    Inserts a League row that is already soft-deleted (is_deleted=True).

    Used by tests that verify soft-deleted rows are correctly hidden from
    GET /league responses, without having to go through the delete endpoint.
    """
    league = LeagueModel(name="Old League", is_deleted=True)
    db_session.add(league)
    db_session.commit()
    db_session.refresh(league)
    return league

@pytest.fixture
def league(league_in_db):
    return league_in_db

@pytest.fixture()
def league_with_season(db_session) -> tuple[LeagueModel, Season]:
    """
    Inserts a League with one child Season and returns both ORM objects.

    This is the fixture that triggers the soft-delete path in delete_league():
    when a league has seasons, it cannot be hard-deleted — it must be
    soft-deleted so historical season data is preserved.

    flush() vs commit():
      db_session.flush() sends the INSERT to the DB and makes the league.id
      available (auto-generated by SQLite), but does not commit. This lets us
      use league.id as the foreign key for the Season row before committing
      both together in a single commit() call.
    """
    from datetime import date

    league = LeagueModel(name="La Liga")
    db_session.add(league)
    db_session.flush()  # get league.id without committing yet

    season = Season(
        league_id=league.id,
        country="Test",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31),
    )
    db_session.add(season)
    db_session.commit()  # persist both league and season together
    db_session.refresh(league)
    return league, season


@pytest.fixture
def player(db_session):
    from src.app.db_models import Player

    player = Player(name="test", birth_date=date(2000, 1, 1), nationality="test")
    db_session.add(player)
    db_session.commit()
    db_session.refresh(player)
    return player


@pytest.fixture
def season(db_session, league_in_db):
    from src.app.db_models import Season


    season = Season(
        league_id=league_in_db.id,
        country="Test",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31),
    )
    db_session.add(season)
    db_session.commit()
    db_session.refresh(season)
    return season


@pytest.fixture
def team(db_session):
    from src.app.db_models import Team

    team = Team(name="Team A", city="City", founded_year=2000, stadium="Stadium")
    db_session.add(team)
    db_session.commit()
    db_session.refresh(team)
    return team


@pytest.fixture
def teams(db_session):
    from src.app.db_models import Team

    t1 = Team(
        name="Team A",
        city="City A",
        founded_year=2000,
        stadium="Stadium A"
    )

    t2 = Team(
        name="Team B",
        city="City B",
        founded_year=2001,
        stadium="Stadium B"
    )

    db_session.add_all([t1, t2])
    db_session.commit()

    return t1, t2

@pytest.fixture
def match(db_session, season, teams):
    from src.app.db_models import Match, MatchParticipant

    t1, t2 = teams

    match = Match(
        season_id=season.id,
        venue="test stadium",
        date=date(2025, 9, 1),
        status="completed"
    )

    db_session.add(match)
    db_session.commit()
    db_session.refresh(match)

    p1 = MatchParticipant(match_id=match.id, team_id=t1.id, is_home=True)
    p2 = MatchParticipant(match_id=match.id, team_id=t2.id, is_home=False)

    db_session.add_all([p1, p2])
    db_session.commit()

    return match