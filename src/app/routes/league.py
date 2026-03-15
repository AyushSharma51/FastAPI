from typing import Annotated
from ..schemas.league_schemas import LeagueResponse , LeagueCreate
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.app.database import get_db

from src.app.services.league_services import create_league, get_all_leagues


router = APIRouter(prefix="/league", tags=["League"])

@router.get("", response_model_exclude_none=True,)
def list_league(db: Annotated[Session, Depends(get_db)]):
    return get_all_leagues(db)

@router.post("", response_model= LeagueResponse)
def create_a_new_league(league:LeagueCreate,db: Annotated[Session, Depends(get_db)]):
        
    return create_league(db=db,
        name=league.name,
        country=league.country,)
        
