from typing import Annotated, List
from ..services.season_services import (
    delete_season,
    list_season,
    create_season,
    patch_season,
    update_season,
)
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session
from src.app.database import get_db
from ..schemas.season_schemas import SeasonResponse, SeasonCreate, SeasonUpdate
from ..security.deps import RoleChecker
from ..db_models import Role


router = APIRouter(prefix="/seasons", tags=["Seasons"])

allow_admin = RoleChecker([Role.ADMIN])
allow_admin_or_editor = RoleChecker([Role.ADMIN, Role.EDITOR])


@router.get(
    "",
    response_model=List[SeasonResponse],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
def list_all_seasons(db: Annotated[Session, Depends(get_db)]):
    return list_season(db)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=SeasonResponse,
    dependencies=[Depends(allow_admin_or_editor)],
)
def create_a_new_season(season: SeasonCreate, db: Annotated[Session, Depends(get_db)]):
    return create_season(db, season)


@router.put(
    "/{season_id}",
    response_model=SeasonResponse,
    dependencies=[Depends(allow_admin_or_editor)],
)
def update_existing_season(
    season_id: Annotated[int, Path(ge=1)],
    season: SeasonCreate,
    db: Annotated[Session, Depends(get_db)],
):
    return update_season(db, season_id, season)


@router.patch(
    "/{season_id}",
    response_model=SeasonResponse,
    dependencies=[Depends(allow_admin_or_editor)],
)
def patch_existing_season(
    season_id: int,
    season: SeasonUpdate,
    db: Annotated[Session, Depends(get_db)],
):
    return patch_season(db, season_id, season)


@router.delete(
    "/{season_id}", status_code=200, dependencies=[Depends(allow_admin_or_editor)]
)
def delete_existing_season(
    season_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    return delete_season(db, season_id)
