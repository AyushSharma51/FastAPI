from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..schemas.match_participants_schemas import MatchParticipantsCreate

from ..db_models import MatchParticipant as MatchParticipantModel

def create_match_participants(db:Session,match_participants:MatchParticipantsCreate):
    match_participants = MatchParticipantModel(**match_participants.model_dump())
    db.add(match_participants)
    db.commit()
    db.refresh(match_participants)
    return match_participants

def list_match_participants(db:Session):
    query=select(MatchParticipantModel).options(
        joinedload(MatchParticipantModel.match),
        joinedload(MatchParticipantModel.team)
    )

    match_participants = db.execute(query).scalars().all()
    return match_participants