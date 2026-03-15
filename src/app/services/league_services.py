from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db_models import League as LeagueModel

def get_all_leagues(db:Session):
    query = select(LeagueModel)
    teams = db.execute(query).scalars().all()
    return teams

def create_league (
    db: Session, name: str, country: str
):
    """Create a new league"""
    league = LeagueModel(name=name, country=country)
    db.add(league)
    db.commit()
    db.refresh(league)
    return league