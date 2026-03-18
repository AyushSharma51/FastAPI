from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from ..db_models import TeamPlayer as TeamPlayerModel
from ..schemas.team_players_schemas import TeamPlayersCreate


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
