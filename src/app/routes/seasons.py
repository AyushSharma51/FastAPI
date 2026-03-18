from typing import Annotated, List
from ..services.season_services import list_season, create_season
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.app.database import get_db
from ..schemas.season_schemas import SeasonResponse, SeasonCreate


router = APIRouter(prefix="/seasons", tags=["Seasons"])


@router.get("", response_model=List[SeasonResponse], response_model_exclude_none=True, status_code=status.HTTP_200_OK)
def list_all_seasons(db: Annotated[Session, Depends(get_db)]):
    return list_season(db)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=SeasonResponse)
def create_a_new_season(season: SeasonCreate, db: Annotated[Session, Depends(get_db)]):
    return create_season(db,season )

