from datetime import date
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

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
)
from ..services.player_services import get_player_cumulative_stats
from ..services.team_services import (
    create_team_players,
    delete_team_player,
    get_all_team_players,
    get_team_player_by_id,
    update_team_player,
)
from ..schemas.common_schemas import PaginationParams

#  SEPARATE ROUTERS
player_router = APIRouter(prefix="/players", tags=["Players"])
team_player_router = APIRouter(prefix="/team-players", tags=["Team Players"])
stats_router = APIRouter(prefix="/player-stats", tags=["Player Stats"])


# ================== PLAYERS ==================


@player_router.get("")
def list_all_players(
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends()],
    name: Optional[str] = None,
):
    return get_all_players(db, pagination, name)


@player_router.post("", response_model=PlayerResponse, status_code=201)
def create_a_new_player(
    player: PlayerCreate,
    db: Annotated[Session, Depends(get_db)],
):
    return create_a_player(db, player)


@player_router.get("/{player_id}", response_model=PlayerResponse)
def get_single_player(player_id: int, db: Annotated[Session, Depends(get_db)]):
    return get_player_by_id(db, player_id)


@player_router.put("/{player_id}", response_model=PlayerResponse)
def update_existing_player(
    player_id: int, player: PlayerCreate, db: Annotated[Session, Depends(get_db)]
):
    return update_player(db, player_id, player)


@player_router.patch("/{player_id}", response_model=PlayerResponse)
def patch_existing_player(
    player_id: int, player: PlayerUpdate, db: Annotated[Session, Depends(get_db)]
):
    return patch_player(db, player_id, player)


@player_router.delete("/{player_id}", status_code=200)
def delete_existing_player(player_id: int, db: Annotated[Session, Depends(get_db)]):
    return delete_player(db, player_id)


@player_router.get(
    "/{player_id}/stats",
    response_model=PlayerCumulativeStatsResponse,
)
def get_cumulative_stats(
    player_id: int,
    db: Annotated[Session, Depends(get_db)],
    year: Optional[int] = Query(default=None),
    league_name: Optional[str] = Query(default=None),
    team_id: Optional[int] = Query(default=None),
    from_date: Optional[date] = Query(default=None),
    to_date: Optional[date] = Query(default=None),
):
    return get_player_cumulative_stats(
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
)
def create_new_team_players(
    team_players: TeamPlayersCreate,
    db: Annotated[Session, Depends(get_db)],
):
    return create_team_players(db, team_players)


@team_player_router.get("")
def list_all_team_players(
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends()],
):
    return get_all_team_players(db, pagination)


@team_player_router.get("/{team_player_id}", response_model=TeamPlayersResponse)
def get_single_team_player(
    team_player_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    return get_team_player_by_id(db, team_player_id)


@team_player_router.patch("/{team_player_id}", response_model=TeamPlayersResponse)
def patch_team_player(
    team_player_id: int,
    data: TeamPlayersUpdate,
    db: Annotated[Session, Depends(get_db)],
):
    return update_team_player(db, team_player_id, data)


@team_player_router.delete("/{team_player_id}", status_code=200)
def delete_team_player_route(
    team_player_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    return delete_team_player(db, team_player_id)


# ================== PLAYER STATS ==================


@stats_router.get("/{stat_id}", response_model=PlayerMatchStatsResponse)
def get_single_player_stat(
    stat_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    return get_player_stat_by_id(db, stat_id)


@stats_router.patch("/{stat_id}", response_model=PlayerMatchStatsResponse)
def patch_player_stat(
    stat_id: int,
    data: PlayerMatchStatsUpdate,
    db: Annotated[Session, Depends(get_db)],
):
    return update_player_stat(db, stat_id, data)


@stats_router.delete("/{stat_id}", status_code=200)
def delete_player_stat_route(
    stat_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    return delete_player_stat(db, stat_id)
