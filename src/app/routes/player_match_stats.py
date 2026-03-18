from typing import Annotated, List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..services.player_match_stats_services import (
    create_player_stats,
    list_player_stats,
)
from src.app.database import get_db
from ..schemas.player_match_stats_schemas import (
    PlayerMatchStatsCreate,
    PlayerMatchStatsResponse,
)


router = APIRouter(prefix="/player_match_stats", tags=["Player Match Stats"])


@router.post(
    "", response_model=PlayerMatchStatsResponse, status_code=status.HTTP_201_CREATED
)
def create_new_player_stats(
    player_stats: PlayerMatchStatsCreate, db: Annotated[Session, Depends(get_db)]
):
    return create_player_stats(db, player_stats)


@router.get(
    "",
    response_model=List[PlayerMatchStatsResponse],             #What if match is Upcoming?/??
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
def list_all_player_stats(db: Annotated[Session, Depends(get_db)]):
    return list_player_stats(db)
