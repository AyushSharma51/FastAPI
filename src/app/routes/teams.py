from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from datetime import date
from ..database import get_db
from ..schemas.team_schemas import TeamCreate, TeamResponse, TeamCumulativeStatsResponse, TeamUpdate
from ..services.team_services import (
    create_team,
    delete_team,
    get_all_teams,
    get_team_by_id,
    get_team_cumulative_stats,
    patch_team,
    update_team,
)

# --------------------------------------------ROUTES----------------------------------------------------------------------

router = APIRouter(prefix="/teams", tags=["Teams"])

@router.get("/{team_id}", response_model=TeamResponse)
def get_single_team(
    team_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    return get_team_by_id(db, team_id)

@router.get("", status_code=status.HTTP_200_OK)
def list_all_teams(db: Annotated[Session, Depends(get_db)]):
    return get_all_teams(db)

# ------------------------------------------POST(CREATE)-------------------------------------------------------------------
@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_new_team(team: TeamCreate, db: Annotated[Session, Depends(get_db)]):
    """Create a new team"""
    return create_team(db, team)

#--------------------------------------------PUT(REPLACE)------------------------------------------------------------------

@router.put("/{team_id}", response_model=TeamResponse)
def update_existing_team(
    team_id: int,
    team: TeamCreate,
    db: Annotated[Session, Depends(get_db)]
):
    return update_team(db, team_id, team)

#---------------------------------------------PATCH(UPDATE)-----------------------------------------------------------------

@router.patch("/{team_id}", response_model=TeamResponse)
def patch_existing_team(
    team_id: int,
    team: TeamUpdate,
    db: Annotated[Session, Depends(get_db)]
):
    return patch_team(db, team_id, team)

#-------------------------------------------------DELETE--------------------------------------------------------------------

@router.delete("/{team_id}", status_code=200)
def delete_existing_team(
    team_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    return delete_team(db, team_id)

#---------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------Team Cumulative Stats-------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------

@router.get(
    "/{team_id}/stats",
    response_model=TeamCumulativeStatsResponse,
    status_code=status.HTTP_200_OK,
)
def get_cumulative_stats(
    team_id: int,
    db: Annotated[Session, Depends(get_db)],
    year: Optional[int] = Query(default=None),
    league_name: Optional[str] = Query(default=None),
    season_id: Optional[int] = Query(default=None),
    from_date: Optional[date] = Query(default=None),
    to_date: Optional[date] = Query(default=None),
):
    return get_team_cumulative_stats(
        db=db,
        team_id=team_id,
        year=year,
        league_name=league_name,
        season_id=season_id,
        from_date=from_date,
        to_date=to_date,
    )