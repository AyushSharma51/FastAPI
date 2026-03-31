from typing import Annotated, Optional
from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.common_schemas import PaginationParams
from ..database import get_db
from ..schemas.team_schemas import (
    TeamCreate,
    TeamResponse,
    TeamCumulativeStatsResponse,
    TeamUpdate,
)
from ..services.team_services import (
    create_team,
    delete_team,
    get_all_teams,
    get_team_by_id,
    get_team_cumulative_stats,
    patch_team,
    update_team,
)
from ..security.deps import RoleChecker
from ..db_models import Role


# -------------------------------------------- ROUTES --------------------------------------------

router = APIRouter(prefix="/teams", tags=["Teams"])

allow_admin = RoleChecker([Role.ADMIN])
allow_admin_or_editor = RoleChecker([Role.ADMIN, Role.EDITOR])


# ================== GET SINGLE ==================

@router.get("/{team_id}", response_model=TeamResponse)
async def get_single_team(
    team_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Get team by ID."""
    return await get_team_by_id(db, team_id)


# ================== GET ALL ==================

@router.get("")
async def list_all_teams(
    db: Annotated[AsyncSession, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends()],
    name: Optional[str] = None,
):
    """List all teams with optional name filter."""
    return await get_all_teams(db, pagination, name)


# ================== CREATE ==================

@router.post(
    "",
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(allow_admin_or_editor)],
)
async def create_new_team(
    team: TeamCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new team (Admin/Editor only)."""
    return await create_team(db, team)


# ================== PUT (REPLACE) ==================

@router.put(
    "/{team_id}",
    response_model=TeamResponse,
    dependencies=[Depends(allow_admin_or_editor)],
)
async def update_existing_team(
    team_id: int,
    team: TeamCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Replace team details completely."""
    return await update_team(db, team_id, team)


# ================== PATCH ==================

@router.patch(
    "/{team_id}",
    response_model=TeamResponse,
    dependencies=[Depends(allow_admin_or_editor)],
)
async def patch_existing_team(
    team_id: int,
    team: TeamUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Partially update team."""
    return await patch_team(db, team_id, team)


# ================== DELETE ==================

@router.delete(
    "/{team_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(allow_admin_or_editor)],
)
async def delete_existing_team(
    team_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete a team."""
    return await delete_team(db, team_id)


# ================== TEAM CUMULATIVE STATS ==================

@router.get(
    "/{team_id}/stats",
    response_model=TeamCumulativeStatsResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(allow_admin_or_editor)],
)
async def get_cumulative_stats(
    team_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    year: Optional[int] = Query(default=None),
    league_name: Optional[str] = Query(default=None),
    season_id: Optional[int] = Query(default=None),
    from_date: Optional[date] = Query(default=None),
    to_date: Optional[date] = Query(default=None),
):
    """
    Get cumulative stats for a team with filters.
    """
    return await get_team_cumulative_stats(
        db=db,
        team_id=team_id,
        year=year,
        league_name=league_name,
        season_id=season_id,
        from_date=from_date,
        to_date=to_date,
    )