from sqlalchemy import select
from sqlalchemy.orm import Session
from ..db_models import Team as TeamModel
from ..schemas.team_schemas import TeamCreate


def create_team(db: Session, team: TeamCreate):
    """Create a new team"""
    team = TeamModel(**team.model_dump())
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


def get_all_teams(db: Session):
    query = select(TeamModel)
    teams = db.execute(query).scalars().all()
    return teams
