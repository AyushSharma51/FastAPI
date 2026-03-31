from typing import Annotated, List

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.database import get_db
from src.app.services.league_services import (
    create_league,
    delete_league,
    get_all_leagues,
    league_update,
)

from ..db_models import Role
from ..schemas.league_schemas import League, LeagueCreate, LeagueResponse
from ..security.deps import RoleChecker

router = APIRouter(prefix="/league", tags=["League"])

allow_admin = RoleChecker([Role.ADMIN])
allow_admin_or_editor = RoleChecker([Role.ADMIN, Role.EDITOR])


# ------------------------------------ GET ALL LEAGUES ------------------------------------

@router.get(
    "",
    response_model=List[LeagueResponse],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def list_league(
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get all active (non-deleted) leagues.
    """
    return await get_all_leagues(db)


# ------------------------------------ CREATE LEAGUE ------------------------------------

@router.post(
    "",
    response_model=LeagueResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(allow_admin_or_editor)],
)
async def create_a_new_league(
    league: LeagueCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Create a new league.

    Requires:
    - ADMIN or EDITOR role
    """
    return await create_league(db, league)


# ------------------------------------ UPDATE LEAGUE ------------------------------------

@router.patch(
    "/{league_id}",
    response_model=LeagueResponse,
    response_model_exclude_none=True,
    dependencies=[Depends(allow_admin_or_editor)],
)
async def update_league(
    league_id: Annotated[int, Path(ge=1, title="League ID")],
    league: League,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Update league details.

    Requires:
    - ADMIN or EDITOR role
    """
    return await league_update(db, league_id, league)


# ------------------------------------ DELETE LEAGUE ------------------------------------

@router.delete(
    "/{league_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(allow_admin_or_editor)],
)
async def delete_league_route(
    league_id: Annotated[int, Path(ge=1, title="League ID")],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Delete a league.

    - Soft delete if linked to seasons
    - Hard delete otherwise

    Requires:
    - ADMIN or EDITOR role
    """
    return await delete_league(db, league_id)