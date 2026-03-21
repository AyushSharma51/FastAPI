from typing import Annotated, List
from ..schemas.league_schemas import LeagueResponse, LeagueCreate, League
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session
from src.app.database import get_db
from src.app.services.league_services import create_league, get_all_leagues, league_update, delete_league

router = APIRouter(prefix="/league", tags=["League"])


@router.get(
    "",
    response_model=List[LeagueResponse],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
def list_league(db: Annotated[Session, Depends(get_db)]):
    return get_all_leagues(db)


@router.post("", response_model=LeagueResponse, status_code=status.HTTP_201_CREATED)
def create_a_new_league(league: LeagueCreate, db: Annotated[Session, Depends(get_db)]):

    return create_league(db,league)


# -----------------------------------------------PATCH-------------------------------------------------------------


@router.patch(
    "/{league_id}",
    response_model=LeagueResponse,
    response_model_exclude_none=True,
)
def update_league(
    league_id: Annotated[int, Path(ge=1, title="League ID")],
    league: League,
    db: Annotated[Session, Depends(get_db)],
):
    return league_update(db, league_id, league)

#------------------------------------------------DELETE--------------------------------------------------------------------
@router.delete("/{league_id}", status_code=status.HTTP_200_OK)
def delete_league_route(
    league_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    return delete_league(db, league_id)

