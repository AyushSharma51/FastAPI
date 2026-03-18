from typing import Annotated, List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..services.team_players_services import create_team_players, get_all_team_players
from src.app.database import get_db
from ..schemas.team_players_schemas import TeamPlayersResponse, TeamPlayersCreate


router = APIRouter(prefix="/team_players", tags=["Team Players"])


@router.post(
    "", response_model=TeamPlayersResponse, status_code=status.HTTP_201_CREATED
)
def create_new_team_players(
    team_players: TeamPlayersCreate, db: Annotated[Session, Depends(get_db)]
):
    return create_team_players(db,team_players)

@router.get("", response_model=List[TeamPlayersResponse], response_model_exclude_none= True, status_code=status.HTTP_200_OK)
def list_all_team_players(db:Annotated[Session,Depends(get_db)]):
    return get_all_team_players(db)
