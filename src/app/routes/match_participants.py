from typing import Annotated, List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..services.match_participants_services import create_match_participants, list_match_participants
from src.app.database import get_db
from ..schemas.match_participants_schemas import MatchParticipantsCreate, MatchParticipantsResponse


router = APIRouter(prefix="/match_participants", tags=["Match Participants"])

@router.post("", response_model= MatchParticipantsResponse,status_code=status.HTTP_201_CREATED)
def create_new_match_participants(match_participants: MatchParticipantsCreate, db: Annotated[Session, Depends(get_db)]):
    return create_match_participants(db,match_participants)

@router.get("",response_model=List[MatchParticipantsResponse],response_model_exclude_none=True, status_code=status.HTTP_200_OK )
def list_all_match_participants(db: Annotated[Session, Depends(get_db)]):
    return list_match_participants(db)