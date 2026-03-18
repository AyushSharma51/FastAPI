from typing import Annotated, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.app.schemas.player_schemas import PlayerCreate,PlayerResponse
from ..services.player_services import get_all_players, create_a_player
from src.app.database import get_db



router=APIRouter(prefix="/players", tags=["Players"])

@router.get("", response_model=List[PlayerResponse],status_code=status.HTTP_200_OK, response_model_exclude_none= True)
def list_all_players(db: Annotated[Session, Depends(get_db)]):
    return get_all_players(db)

@router.post("", status_code=status.HTTP_200_OK,response_model=PlayerResponse)
def create_a_new_player(player: PlayerCreate, db: Annotated[Session, Depends(get_db)]):
    
    return create_a_player(db, player)

