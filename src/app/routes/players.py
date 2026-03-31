from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..schemas.player_schemas import (
    PlayerCreate,
    PlayerMatchStatsResponse,
    PlayerMatchStatsUpdate,
    PlayerResponse,
    PlayerCumulativeStatsResponse,
    PlayerUpdate,
)
from ..schemas.team_schemas import (
    TeamPlayersCreate,
    TeamPlayersResponse,
    TeamPlayersUpdate,
)
from ..services.player_services import (
    create_a_player,
    delete_player,
    delete_player_stat,
    get_all_players,
    get_player_by_id,
    get_player_stat_by_id,
    patch_player,
    update_player,
    update_player_stat,
    get_player_cumulative_stats,
)
from ..services.team_services import (
    create_team_players,
    delete_team_player,
    get_all_team_players,
    get_team_player_by_id,
    update_team_player,
)
from ..schemas.common_schemas import PaginationParams
from ..security.deps import RoleChecker
from ..db_models import Role


# ROUTERS
player_router = APIRouter(prefix="/players", tags=["Players"])
team_player_router = APIRouter(prefix="/team-players", tags=["Team Players"])
stats_router = APIRouter(prefix="/player-stats", tags=["Player Stats"])

allow_admin = RoleChecker([Role.ADMIN])
allow_admin_or_editor = RoleChecker([Role.ADMIN, Role.EDITOR])


# ================== PLAYERS ==================

@player_router.get("")
async def list_all_players(
    db: Annotated[AsyncSession, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends()],
    name: Optional[str] = None,
):
    """Get all players with optional name filter."""
    return await get_all_players(db, pagination, name)


@player_router.post(
    "",
    response_model=PlayerResponse,
    status_code=201,
    dependencies=[Depends(allow_admin_or_editor)],
)
async def create_a_new_player(
    player: PlayerCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new player."""
    return await create_a_player(db, player)


@player_router.get("/{player_id}", response_model=PlayerResponse)
async def get_single_player(
    player_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get player by ID."""
    return await get_player_by_id(db, player_id)


@player_router.put(
    "/{player_id}",
    response_model=PlayerResponse,
    dependencies=[Depends(allow_admin_or_editor)],
)
async def update_existing_player(
    player_id: int,
    player: PlayerCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Replace player details."""
    return await update_player(db, player_id, player)


@player_router.patch(
    "/{player_id}",
    response_model=PlayerResponse,
    dependencies=[Depends(allow_admin_or_editor)],
)
async def patch_existing_player(
    player_id: int,
    player: PlayerUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Partially update player."""
    return await patch_player(db, player_id, player)


@player_router.delete(
    "/{player_id}",
    status_code=200,
    dependencies=[Depends(allow_admin_or_editor)],
)
async def delete_existing_player(
    player_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete a player."""
    return await delete_player(db, player_id)


@player_router.get(
    "/{player_id}/stats",
    response_model=PlayerCumulativeStatsResponse,
)
async def get_cumulative_stats(
    player_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    year: Optional[int] = Query(default=None),
    league_name: Optional[str] = Query(default=None),
    team_id: Optional[int] = Query(default=None),
    from_date: Optional[date] = Query(default=None),
    to_date: Optional[date] = Query(default=None),
):
    """Get cumulative stats for a player with filters."""
    return await get_player_cumulative_stats(
        db=db,
        player_id=player_id,
        year=year,
        league_name=league_name,
        team_id=team_id,
        from_date=from_date,
        to_date=to_date,
    )


# ================== TEAM PLAYERS ==================

@team_player_router.post(
    "",
    response_model=TeamPlayersResponse,
    status_code=201,
    dependencies=[Depends(allow_admin_or_editor)],
)
async def create_new_team_players(
    team_players: TeamPlayersCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Assign player to team."""
    return await create_team_players(db, team_players)


@team_player_router.get("")
async def list_all_team_players(
    db: Annotated[AsyncSession, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends()],
):
    """List all team-player relationships."""
    return await get_all_team_players(db, pagination)


@team_player_router.get("/{team_player_id}", response_model=TeamPlayersResponse)
async def get_single_team_player(
    team_player_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get team-player mapping by ID."""
    return await get_team_player_by_id(db, team_player_id)


@team_player_router.patch(
    "/{team_player_id}",
    response_model=TeamPlayersResponse,
    dependencies=[Depends(allow_admin_or_editor)],
)
async def patch_team_player(
    team_player_id: int,
    data: TeamPlayersUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update team-player mapping."""
    return await update_team_player(db, team_player_id, data)


@team_player_router.delete(
    "/{team_player_id}",
    status_code=200,
    dependencies=[Depends(allow_admin_or_editor)],
)
async def delete_team_player_route(
    team_player_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete team-player mapping."""
    return await delete_team_player(db, team_player_id)


# ================== PLAYER STATS ==================

@stats_router.get("/{stat_id}", response_model=PlayerMatchStatsResponse)
async def get_single_player_stat(
    stat_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get player match stat by ID."""
    return await get_player_stat_by_id(db, stat_id)


@stats_router.patch(
    "/{stat_id}",
    response_model=PlayerMatchStatsResponse,
    dependencies=[Depends(allow_admin_or_editor)],
)
async def patch_player_stat(
    stat_id: int,
    data: PlayerMatchStatsUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update player match stat."""
    return await update_player_stat(db, stat_id, data)


@stats_router.delete(
    "/{stat_id}",
    status_code=200,
    dependencies=[Depends(allow_admin_or_editor)],
)
async def delete_player_stat_route(
    stat_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete player match stat."""
    return await delete_player_stat(db, stat_id)