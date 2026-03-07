from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from .schema import Match,Sport, Winner, Status
from typing import List
from datetime import date as dt_date

from .db_models import Base

DATABASE_URL = "sqlite:///./matches.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


def create_tables():
    Base.metadata.create_all(engine)


def get_db():
    with Session(engine) as session:
        yield session



INITIAL_DATA: List[Match] = [
    Match(
        id=1,
        home_team="Arsenal",
        away_team="Chelsea",
        sport=Sport.football,
        date=dt_date(2025, 10, 21),
        status=Status.completed,
        winner=Winner.draw,
        venue="Emirates Stadium",
    ),
    Match(
        id=2,
        home_team="Lakers",
        away_team="Warriors",
        sport=Sport.basketball,
        date=dt_date(2025, 11, 15),
        status=Status.completed,
        winner=Winner.home_team,
        venue="Crypto.com Arena",
    ),
    Match(
        id=3,
        home_team="Real Madrid",
        away_team="Barcelona",
        sport=Sport.football,
        date=dt_date(2026, 4, 10),
        status=Status.completed,
        winner=Winner.draw,
        venue="Santiago Bernabeu",
    ),
    Match(
        id=4,
        home_team="Knicks",
        away_team="Celtics",
        sport=Sport.basketball,
        date=dt_date(2027, 3, 5),
        status=Status.upcoming,
        winner=None,
        venue="Madison Square Garden",
    ),
    Match(
        id=5,
        home_team="Yankees",
        away_team="Red Sox",
        sport=Sport.baseball,
        date=dt_date(2025, 8, 10),
        status=Status.abandoned,
        winner=None,
        venue="Yankee Stadium",
    ),
    Match(
        id=6,
        home_team="India",
        away_team="Pakistan",
        sport=Sport.cricket,
        date=dt_date(2026, 3, 24),
        status=Status.completed,
        winner=Winner.home_team,
        venue="Narendra Modi Stadium",
    ),
    Match(
        id=7,
        home_team="Lakers",
        away_team="Warriors",
        sport=Sport.basketball,
        date=dt_date(2025, 1, 15),
        status=Status.completed,
        winner=Winner.away_team,
        venue="Crypto.com Arena",
    ),
]