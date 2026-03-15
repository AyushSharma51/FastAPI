from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.team_schemas import TeamCreate, TeamResponse
from ..services.team_services import create_team, get_all_teams
# --------------------------------------------ROUTES----------------------------------------------------------------------
router = APIRouter(prefix="/teams", tags=["Teams"])


@router.get("", status_code=status.HTTP_200_OK)
def list_all_teams(db: Annotated[Session, Depends(get_db)]):
    return get_all_teams(db)

# ------------------------------------------POST(CREATE)-------------------------------------------------------------------
@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_new_team(team: TeamCreate, db: Annotated[Session, Depends(get_db)]):
    """Create a new team"""
    return create_team(
        db=db,
        name=team.name,
        city=team.city,
        founded_year=team.founded_year,
        stadium=team.stadium,
    )