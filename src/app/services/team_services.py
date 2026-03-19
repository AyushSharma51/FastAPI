from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from ..db_models import Team as TeamModel
from ..schemas.team_schemas import TeamCreate
from ..db_models import TeamPlayer as TeamPlayerModel
from ..schemas.team_schemas import TeamPlayersCreate

# Team Services
#---------------------------------------------------------------------------------------------------------------------

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

#Team Player Services
#-----------------------------------------------------------------------------------------------------------------------

def create_team_players(db: Session, team_players: TeamPlayersCreate):

    team_players = TeamPlayerModel(**team_players.model_dump())
    db.add(team_players)
    db.commit()
    db.refresh(team_players)
    return team_players


def get_all_team_players(db: Session):
    query = select(TeamPlayerModel).options(
        joinedload(TeamPlayerModel.team),
        joinedload(TeamPlayerModel.season),
        joinedload(TeamPlayerModel.player),
    )

    team_players = db.execute(query).scalars().all()
    return team_players

