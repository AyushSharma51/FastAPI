from sqlalchemy import select
from sqlalchemy.orm import Session
from ..db_models import TeamModel


def create_team(
    db: Session, name: str, city: str, founded_year: int, stadium: str | None = None
):
    """Create a new team"""
    team = TeamModel(name=name, city=city, founded_year=founded_year, stadium=stadium)
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


def get_all_teams(db: Session):
    query = select(TeamModel)
    teams = db.execute(query).scalars().all()
    return teams
