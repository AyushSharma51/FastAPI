from datetime import date as dt_date

from sqlalchemy import select
from sqlalchemy.orm import Session
from .schema import Match, Sport, Status, Winner

from .database import engine, create_tables
from .db_models import MatchModel


SEED_MATCHES = [
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


def seed():
    create_tables()

    with Session(engine) as db:
        existing = db.execute(select(MatchModel)).scalars().first()  
        if existing:                                                   
            print("Database already seeded — skipping.")              
            return                                                     

        db.add_all(SEED_MATCHES)  
        db.commit()
        print(f"Seeded {len(SEED_MATCHES)} matches.")


if __name__ == "__main__":
    seed()