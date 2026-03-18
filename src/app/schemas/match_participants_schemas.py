from pydantic import BaseModel, Field

from ..schemas.team_schemas import TeamResponse, TeamNameResponse


class MatchParticipants(BaseModel):
    match_id: int = Field(gt=0)
    team_id: int = Field(gt=0)
    is_home: bool
    score: int = Field(ge=0)

    
    class Config:
        from_attributes = True


class MatchParticipantsCreate(MatchParticipants):
    pass


class MatchParticipantsResponse(MatchParticipants):
    id: int


class MatchParticipantResponseforMatch(BaseModel):
    team: TeamResponse
    is_home: bool
    score: int

    class Config:
        from_attributes = True


class MatchParticipantLite(BaseModel):
    team: TeamNameResponse
    is_home: bool
    score: int

    class Config:
        from_attributes = True