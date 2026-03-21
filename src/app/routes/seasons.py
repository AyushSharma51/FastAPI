from typing import Annotated, List
from ..services.season_services import delete_season, list_season, create_season, patch_season, update_season
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.app.database import get_db
from ..schemas.season_schemas import SeasonResponse, SeasonCreate, SeasonUpdate


router = APIRouter(prefix="/seasons", tags=["Seasons"])


@router.get("", response_model=List[SeasonResponse], response_model_exclude_none=True, status_code=status.HTTP_200_OK)
def list_all_seasons(db: Annotated[Session, Depends(get_db)]):
    return list_season(db)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=SeasonResponse)
def create_a_new_season(season: SeasonCreate, db: Annotated[Session, Depends(get_db)]):
    return create_season(db,season )

@router.put("/{season_id}", response_model=SeasonResponse)
def update_existing_season(
    season_id: int,
    season: SeasonCreate,
    db: Annotated[Session, Depends(get_db)],
):
    return update_season(db, season_id, season)

@router.patch("/{season_id}", response_model=SeasonResponse)
def patch_existing_season(
    season_id: int,
    season: SeasonUpdate,
    db: Annotated[Session, Depends(get_db)],
):
    return patch_season(db, season_id, season)

@router.delete("/{season_id}", status_code=200)
def delete_existing_season(
    season_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    return delete_season(db, season_id)