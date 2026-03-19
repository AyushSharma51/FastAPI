from datetime import date
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends,  Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.player_schemas import PlayerCreate, PlayerResponse, PlayerCumulativeStatsResponse
from ..schemas.team_schemas import TeamPlayersCreate, TeamPlayersResponse
from ..services.player_services import create_a_player, get_all_players
from ..services.player_services import get_player_cumulative_stats
from ..services.team_services import create_team_players, get_all_team_players

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
