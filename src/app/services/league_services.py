from sqlalchemy import select
from sqlalchemy.orm import Session

from ..schemas.league_schemas import LeagueCreate

from ..db_models import League as LeagueModel


def get_all_leagues(db: Session):
    query = select(LeagueModel)
    teams = db.execute(query).scalars().all()
    return teams


def create_league(db: Session, league: LeagueCreate):
    """Create a new league"""
    league = LeagueModel(**league.model_dump())
    db.add(league)
    db.commit()
    db.refresh(league)
    return league
