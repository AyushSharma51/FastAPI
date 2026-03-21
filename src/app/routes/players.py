from datetime import date
from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends,   Query, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.player_schemas import PlayerCreate, PlayerMatchStatsResponse, PlayerMatchStatsUpdate, PlayerResponse, PlayerCumulativeStatsResponse, PlayerUpdate
from ..schemas.team_schemas import TeamPlayersCreate, TeamPlayersResponse, TeamPlayersUpdate
from ..services.player_services import create_a_player, delete_player, delete_player_stat, get_all_players, get_player_by_id, get_player_stat_by_id, patch_player, update_player, update_player_stat
from ..services.player_services import get_player_cumulative_stats
from ..services.team_services import create_team_players, delete_team_player, get_all_team_players, get_team_player_by_id, update_team_player

router = APIRouter(prefix="/players", tags=["Players"])


# GET (LIST) -------------------------------------------------------------------


@router.get(
    "",
    response_model=List[PlayerResponse],
    status_code=status.HTTP_200_OK,
    response_model_exclude_none=True,
)
def list_all_players(db: Annotated[Session, Depends(get_db)]):
    return get_all_players(db)


# POST (CREATE) ----------------------------------------------------------------


@router.post("", status_code=status.HTTP_201_CREATED, response_model=PlayerResponse)
def create_a_new_player(
    player: PlayerCreate,
    db: Annotated[Session, Depends(get_db)],
):
    return create_a_player(db, player)

# GET PLAYER BY ID -----------------------------------------------------------

@router.get("/{player_id}", response_model=PlayerResponse)
def get_single_player(
    player_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    return get_player_by_id(db, player_id)

# PUT -------------------------------------------------------------------------

@router.put("/{player_id}", response_model=PlayerResponse)
def update_existing_player(
    player_id: int,
    player: PlayerCreate,
    db: Annotated[Session, Depends(get_db)]
):
    return update_player(db, player_id, player)

# PATCH -----------------------------------------------------------------------

@router.patch("/{player_id}", response_model=PlayerResponse)
def patch_existing_player(
    player_id: int,
    player: PlayerUpdate,
    db: Annotated[Session, Depends(get_db)]
):
    return patch_player(db, player_id, player)

# DELETE -----------------------------------------------------------------------

@router.delete("/{player_id}", status_code=200)
def delete_existing_player(
    player_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    return delete_player(db, player_id)

# GET /{player_id}/stats -------------------------------------------------------


@router.get(
    "/{player_id}/stats",
    response_model=PlayerCumulativeStatsResponse,
    status_code=status.HTTP_200_OK,
)
def get_cumulative_stats(
    player_id: int,
    db: Annotated[Session, Depends(get_db)],
    year: Optional[int] = Query(
        default=None, description="Filter by season year, e.g. 2018"
    ),
    league_name: Optional[str] = Query(
        default=None, description="Filter by league name, e.g. 'Premier League'"
    ),
    team_id: Optional[int] = Query(
        default=None, description="Filter stats to a specific team"
    ),
    from_date: Optional[date] = Query(
        default=None, description="Match date from (inclusive)"
    ),
    to_date: Optional[date] = Query(
        default=None, description="Match date to (inclusive)"
    ),
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


# ROSTERS ----------------------------------------------------------------------


@router.post(
    "/teams",
    response_model=TeamPlayersResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_team_players(
    team_players: TeamPlayersCreate,
    db: Annotated[Session, Depends(get_db)],
):
    return create_team_players(db, team_players)


@router.get(
    "/teams",
    response_model=List[TeamPlayersResponse],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
def list_all_team_players(
    db: Annotated[Session, Depends(get_db)],
):
    return get_all_team_players(db)

@router.get(
    "/teams/{team_player_id}",
    response_model=TeamPlayersResponse,
    status_code=200,
)
def get_single_team_player(
    team_player_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    return get_team_player_by_id(db, team_player_id)

@router.patch(
    "/teams/{team_player_id}",
    response_model=TeamPlayersResponse,
    status_code=200,
)
def patch_team_player(
    team_player_id: int,
    data: TeamPlayersUpdate,
    db: Annotated[Session, Depends(get_db)],
):
    return update_team_player(db, team_player_id, data)

@router.delete(
    "/teams/{team_player_id}",
    status_code=200,
)
def delete_team_player_route(
    team_player_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    return delete_team_player(db, team_player_id)


@router.get(
    "/matches/players/stats/{stat_id}",
    response_model=PlayerMatchStatsResponse,
    status_code=200,
)
def get_single_player_stat(
    stat_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    return get_player_stat_by_id(db, stat_id)

@router.patch(
    "/matches/players/stats/{stat_id}",
    response_model=PlayerMatchStatsResponse,
    status_code=200,
)
def patch_player_stat(
    stat_id: int,
    data: PlayerMatchStatsUpdate,
    db: Annotated[Session, Depends(get_db)],
):
    return update_player_stat(db, stat_id, data)


@router.delete(
    "/matches/players/stats/{stat_id}",
    status_code=200,
)
def delete_player_stat_route(
    stat_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    return delete_player_stat(db, stat_id)
