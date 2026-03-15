from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..services.standings_services import create_standing, list_standings
from src.app.database import get_db
from ..schemas.standings_schemas import StandingsResponse, StandingsCreate


router = APIRouter(prefix="/standings", tags=["Standings"])

@router.post("", response_model= StandingsResponse,status_code=status.HTTP_201_CREATED)
def create_new_standing(standing: StandingsCreate, db: Annotated[Session, Depends(get_db)]):
    return create_standing(
        db=db,
        season_id= standing.season_id,
        team_id=standing.team_id,
        matches_played= standing.matches_played,
        wins=standing.wins,
        draws=standing.draws,
        losses=standing.losses,
        points= standing.points,
    )

@router.get("",response_model_exclude_none=True, status_code=status.HTTP_201_CREATED, response_model=StandingsResponse)
def list_all_standings(db: Annotated[Session, Depends(get_db)]):
    return list_standings(db)