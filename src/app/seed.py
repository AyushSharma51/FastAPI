"""
seed.py — Populate the football league database with sample data.
Run from the project root:  python -m app.seed  (adjust import path as needed)

Standings are intentionally skipped as requested.
"""

from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# ---------------------------------------------------------------------------
# If you run this as a standalone script adjust the import below to match
# your package structure, e.g.:
#   from app.db_models import ...
# ---------------------------------------------------------------------------
from .db_models import Role  # <-- Added
from .db_models import User  # <-- Added
from .db_models import (
    Base,
    League,
    Match,
    MatchParticipant,
    Player,
    PlayerMatchStat,
    Season,
    Team,
    TeamPlayer,
)

# Import the password hasher from your auth module
from .security.auth import get_password_hash  # <-- Added

DATABASE_URL = "sqlite:///./matches.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)


def seed():
    Base.metadata.create_all(engine)

    with Session(engine) as session:

        # ------------------------------------------------------------------ #
        # Guard – skip if data already exists                                #
        # ------------------------------------------------------------------ #
        if session.query(League).first():
            print("Database already seeded – skipping.")
            return

        # ------------------------------------------------------------------ #
        # Seed Initial Admin User                                            #
        # ------------------------------------------------------------------ #
        admin_exists = session.query(User).filter(User.username == "admin").first()
        if not admin_exists:
            hashed_pwd = get_password_hash("admin123")
            admin_user = User(
                username="admin", hashed_password=hashed_pwd, role=Role.ADMIN
            )
            session.add(admin_user)
            session.flush()
            print("👤 Admin user created (Username: admin, Password: admin123)")

        # ------------------------------------------------------------------ #
        # Leagues                                                            #
        # ------------------------------------------------------------------ #
        premier_league = League(name="Premier League")
        la_liga = League(name="La Liga")
        session.add_all([premier_league, la_liga])
        session.flush()  # assign IDs before referencing them

        # ------------------------------------------------------------------ #
        # Seasons                                                            #
        # ------------------------------------------------------------------ #
        pl_season = Season(
            league=premier_league,
            country="England",
            start_date=date(2024, 8, 17),
            end_date=date(2025, 5, 25),
        )
        ll_season = Season(
            league=la_liga,
            country="Spain",
            start_date=date(2024, 8, 18),
            end_date=date(2025, 5, 25),
        )
        session.add_all([pl_season, ll_season])
        session.flush()

        # ------------------------------------------------------------------ #
        # Teams                                                              #
        # ------------------------------------------------------------------ #
        man_city = Team(
            name="Manchester City",
            city="Manchester",
            founded_year=1880,
            stadium="Etihad Stadium",
        )
        arsenal = Team(
            name="Arsenal",
            city="London",
            founded_year=1886,
            stadium="Emirates Stadium",
        )
        liverpool = Team(
            name="Liverpool",
            city="Liverpool",
            founded_year=1892,
            stadium="Anfield",
        )
        chelsea = Team(
            name="Chelsea",
            city="London",
            founded_year=1905,
            stadium="Stamford Bridge",
        )
        barcelona = Team(
            name="FC Barcelona",
            city="Barcelona",
            founded_year=1899,
            stadium="Estadi Olímpic Lluís Companys",
        )
        real_madrid = Team(
            name="Real Madrid",
            city="Madrid",
            founded_year=1902,
            stadium="Santiago Bernabéu",
        )
        session.add_all([man_city, arsenal, liverpool, chelsea, barcelona, real_madrid])
        session.flush()

        # ------------------------------------------------------------------ #
        # Players                                                            #
        # ------------------------------------------------------------------ #
        # Premier League players
        haaland = Player(
            name="Erling Haaland", birth_date=date(2000, 7, 21), nationality="Norwegian"
        )
        de_bruyne = Player(
            name="Kevin De Bruyne", birth_date=date(1991, 6, 28), nationality="Belgian"
        )
        saka = Player(
            name="Bukayo Saka", birth_date=date(2001, 9, 5), nationality="English"
        )
        odegaard = Player(
            name="Martin Ødegaard",
            birth_date=date(1998, 12, 17),
            nationality="Norwegian",
        )
        salah = Player(
            name="Mohamed Salah", birth_date=date(1992, 6, 15), nationality="Egyptian"
        )
        nunez = Player(
            name="Darwin Núñez", birth_date=date(1999, 6, 24), nationality="Uruguayan"
        )
        palmer = Player(
            name="Cole Palmer", birth_date=date(2002, 5, 6), nationality="English"
        )
        jackson = Player(
            name="Nicolas Jackson",
            birth_date=date(2001, 6, 20),
            nationality="Senegalese",
        )
        # La Liga players
        yamal = Player(
            name="Lamine Yamal", birth_date=date(2007, 7, 13), nationality="Spanish"
        )
        lewandowski = Player(
            name="Robert Lewandowski",
            birth_date=date(1988, 8, 21),
            nationality="Polish",
        )
        vinicius = Player(
            name="Vinícius Jr.", birth_date=date(2000, 7, 12), nationality="Brazilian"
        )
        bellingham = Player(
            name="Jude Bellingham", birth_date=date(2003, 6, 29), nationality="English"
        )

        session.add_all(
            [
                haaland,
                de_bruyne,
                saka,
                odegaard,
                salah,
                nunez,
                palmer,
                jackson,
                yamal,
                lewandowski,
                vinicius,
                bellingham,
            ]
        )
        session.flush()

        # ------------------------------------------------------------------ #
        # Rosters (TeamPlayer)                                               #
        # ------------------------------------------------------------------ #
        pl_roster = [
            TeamPlayer(
                team=man_city, player=haaland, season=pl_season, jersey_number=9
            ),
            TeamPlayer(
                team=man_city, player=de_bruyne, season=pl_season, jersey_number=17
            ),
            TeamPlayer(team=arsenal, player=saka, season=pl_season, jersey_number=7),
            TeamPlayer(
                team=arsenal, player=odegaard, season=pl_season, jersey_number=8
            ),
            TeamPlayer(
                team=liverpool, player=salah, season=pl_season, jersey_number=11
            ),
            TeamPlayer(team=liverpool, player=nunez, season=pl_season, jersey_number=9),
            TeamPlayer(team=chelsea, player=palmer, season=pl_season, jersey_number=20),
            TeamPlayer(
                team=chelsea, player=jackson, season=pl_season, jersey_number=15
            ),
        ]
        ll_roster = [
            TeamPlayer(
                team=barcelona, player=yamal, season=ll_season, jersey_number=27
            ),
            TeamPlayer(
                team=barcelona, player=lewandowski, season=ll_season, jersey_number=9
            ),
            TeamPlayer(
                team=real_madrid, player=vinicius, season=ll_season, jersey_number=7
            ),
            TeamPlayer(
                team=real_madrid, player=bellingham, season=ll_season, jersey_number=5
            ),
        ]
        session.add_all(pl_roster + ll_roster)
        session.flush()

        # ------------------------------------------------------------------ #
        # Matches                                                            #
        # ------------------------------------------------------------------ #
        # --- Premier League ---
        match1 = Match(
            season=pl_season,
            venue="Etihad Stadium",
            date=date(2024, 8, 24),
            status="completed",
        )
        match2 = Match(
            season=pl_season,
            venue="Emirates Stadium",
            date=date(2024, 9, 1),
            status="completed",
        )
        match3 = Match(
            season=pl_season,
            venue="Anfield",
            date=date(2024, 9, 14),
            status="completed",
        )
        match4 = Match(
            season=pl_season,
            venue="Stamford Bridge",
            date=date(2027, 9, 22),
            status="upcoming",
        )
        # --- La Liga ---
        match5 = Match(
            season=ll_season,
            venue="Estadi Olímpic Lluís Companys",
            date=date(2024, 8, 25),
            status="completed",
        )
        match6 = Match(
            season=ll_season,
            venue="Santiago Bernabéu",
            date=date(2024, 9, 7),
            status="completed",
        )

        session.add_all([match1, match2, match3, match4, match5, match6])
        session.flush()

        # ------------------------------------------------------------------ #
        # Match Participants                                                 #
        # ------------------------------------------------------------------ #
        session.add_all(
            [
                # match1: Man City 3 – 1 Chelsea
                MatchParticipant(match=match1, team=man_city, is_home=True, score=3),
                MatchParticipant(match=match1, team=chelsea, is_home=False, score=1),
                # match2: Arsenal 2 – 2 Liverpool
                MatchParticipant(match=match2, team=arsenal, is_home=True, score=2),
                MatchParticipant(match=match2, team=liverpool, is_home=False, score=2),
                # match3: Liverpool 1 – 0 Man City
                MatchParticipant(match=match3, team=liverpool, is_home=True, score=1),
                MatchParticipant(match=match3, team=man_city, is_home=False, score=0),
                # match4: Chelsea vs Arsenal — scheduled, no score yet
                MatchParticipant(match=match4, team=chelsea, is_home=True, score=None),
                MatchParticipant(match=match4, team=arsenal, is_home=False, score=None),
                # match5: Barcelona 4 – 1 Real Madrid
                MatchParticipant(match=match5, team=barcelona, is_home=True, score=4),
                MatchParticipant(
                    match=match5, team=real_madrid, is_home=False, score=1
                ),
                # match6: Real Madrid 2 – 0 Barcelona
                MatchParticipant(match=match6, team=real_madrid, is_home=True, score=2),
                MatchParticipant(match=match6, team=barcelona, is_home=False, score=0),
            ]
        )
        session.flush()

        # ------------------------------------------------------------------ #
        # Player Match Stats (only finished matches)                         #
        # ------------------------------------------------------------------ #
        session.add_all(
            [
                # match1 — Man City 3-1 Chelsea
                PlayerMatchStat(
                    match=match1,
                    player=haaland,
                    team=man_city,
                    goals=2,
                    assists=0,
                    minutes_played=90,
                ),
                PlayerMatchStat(
                    match=match1,
                    player=de_bruyne,
                    team=man_city,
                    goals=1,
                    assists=1,
                    minutes_played=82,
                ),
                PlayerMatchStat(
                    match=match1,
                    player=palmer,
                    team=chelsea,
                    goals=1,
                    assists=0,
                    minutes_played=90,
                ),
                PlayerMatchStat(
                    match=match1,
                    player=jackson,
                    team=chelsea,
                    goals=0,
                    assists=0,
                    minutes_played=75,
                ),
                # match2 — Arsenal 2-2 Liverpool
                PlayerMatchStat(
                    match=match2,
                    player=saka,
                    team=arsenal,
                    goals=1,
                    assists=1,
                    minutes_played=90,
                ),
                PlayerMatchStat(
                    match=match2,
                    player=odegaard,
                    team=arsenal,
                    goals=1,
                    assists=0,
                    minutes_played=90,
                ),
                PlayerMatchStat(
                    match=match2,
                    player=salah,
                    team=liverpool,
                    goals=1,
                    assists=1,
                    minutes_played=90,
                ),
                PlayerMatchStat(
                    match=match2,
                    player=nunez,
                    team=liverpool,
                    goals=1,
                    assists=0,
                    minutes_played=88,
                ),
                # match3 — Liverpool 1-0 Man City
                PlayerMatchStat(
                    match=match3,
                    player=salah,
                    team=liverpool,
                    goals=1,
                    assists=0,
                    minutes_played=90,
                ),
                PlayerMatchStat(
                    match=match3,
                    player=nunez,
                    team=liverpool,
                    goals=0,
                    assists=1,
                    minutes_played=90,
                ),
                PlayerMatchStat(
                    match=match3,
                    player=haaland,
                    team=man_city,
                    goals=0,
                    assists=0,
                    minutes_played=90,
                ),
                PlayerMatchStat(
                    match=match3,
                    player=de_bruyne,
                    team=man_city,
                    goals=0,
                    assists=0,
                    minutes_played=79,
                ),
                # match5 — Barcelona 4-1 Real Madrid
                PlayerMatchStat(
                    match=match5,
                    player=lewandowski,
                    team=barcelona,
                    goals=2,
                    assists=1,
                    minutes_played=90,
                ),
                PlayerMatchStat(
                    match=match5,
                    player=yamal,
                    team=barcelona,
                    goals=1,
                    assists=2,
                    minutes_played=90,
                ),
                PlayerMatchStat(
                    match=match5,
                    player=vinicius,
                    team=real_madrid,
                    goals=1,
                    assists=0,
                    minutes_played=90,
                ),
                PlayerMatchStat(
                    match=match5,
                    player=bellingham,
                    team=real_madrid,
                    goals=0,
                    assists=0,
                    minutes_played=85,
                ),
                # match6 — Real Madrid 2-0 Barcelona
                PlayerMatchStat(
                    match=match6,
                    player=bellingham,
                    team=real_madrid,
                    goals=1,
                    assists=1,
                    minutes_played=90,
                ),
                PlayerMatchStat(
                    match=match6,
                    player=vinicius,
                    team=real_madrid,
                    goals=1,
                    assists=0,
                    minutes_played=90,
                ),
                PlayerMatchStat(
                    match=match6,
                    player=lewandowski,
                    team=barcelona,
                    goals=0,
                    assists=0,
                    minutes_played=90,
                ),
                PlayerMatchStat(
                    match=match6,
                    player=yamal,
                    team=barcelona,
                    goals=0,
                    assists=0,
                    minutes_played=78,
                ),
            ]
        )

        session.commit()
        print("✅ Database seeded successfully.")


if __name__ == "__main__":
    seed()
