from typing import Annotated, List

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.database import get_db
from ..services.season_services import (
    delete_season,
    list_season,
    create_season,
    patch_season,
    update_season,
)
from ..schemas.season_schemas import SeasonResponse, SeasonCreate, SeasonUpdate
from ..security.deps import RoleChecker
from ..db_models import Role


router = APIRouter(prefix="/seasons", tags=["Seasons"])

allow_admin = RoleChecker([Role.ADMIN])
allow_admin_or_editor = RoleChecker([Role.ADMIN, Role.EDITOR])


# ================== GET ALL ==================

@router.get(
    "",
    response_model=List[SeasonResponse],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def list_all_seasons(
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get all seasons.
    """
    return await list_season(db)


# ================== CREATE ==================

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=SeasonResponse,
    dependencies=[Depends(allow_admin_or_editor)],
)
async def create_a_new_season(
    season: SeasonCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Create a new season.

    Requires:
    - ADMIN or EDITOR role
    """
    return await create_season(db, season)


# ================== PUT (REPLACE) ==================

@router.put(
    "/{season_id}",
    response_model=SeasonResponse,
    dependencies=[Depends(allow_admin_or_editor)],
)
async def update_existing_season(
    season_id: Annotated[int, Path(ge=1, title="Season ID")],
    season: SeasonCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Replace a season completely.
    """
    return await update_season(db, season_id, season)


# ================== PATCH ==================

@router.patch(
    "/{season_id}",
    response_model=SeasonResponse,
    dependencies=[Depends(allow_admin_or_editor)],
)
async def patch_existing_season(
    season_id: Annotated[int, Path(ge=1, title="Season ID")],
    season: SeasonUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Partially update a season.
    """
    return await patch_season(db, season_id, season)


# ================== DELETE ==================

@router.delete(
    "/{season_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(allow_admin_or_editor)],
)
async def delete_existing_season(
    season_id: Annotated[int, Path(ge=1, title="Season ID")],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Delete a season.

    Requires:
    - ADMIN or EDITOR role
    """
    return await delete_season(db, season_id)