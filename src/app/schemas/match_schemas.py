from datetime import date as dt_date
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from ..schemas.team_schemas import TeamNameResponse, TeamResponse
from ..schemas.season_schemas import SeasonResponsewoLeague


class Status(str, Enum):
    upcoming = "upcoming"
    cancelled = "cancelled"
    abandoned = "abandoned"
    completed = "completed"


# Match participants schema 

class MatchParticipants(BaseModel):
    match_id: int = Field(gt=0)
    team_id: int = Field(gt=0)
    is_home: bool
   

    class Config:
        from_attributes = True


class MatchParticipantsCreate(MatchParticipants):
    pass


class MatchParticipantsResponse(MatchParticipants):
    id: int


class MatchParticipantResponseforMatch(BaseModel):
    team: TeamResponse
    is_home: bool

    class Config:
        from_attributes = True


class MatchParticipantLite(BaseModel):
    team: TeamNameResponse
    is_home: bool
    
    class Config:
        from_attributes = True


# Matches Schema

class Match(BaseModel):

    season_id: int
    venue: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100,
        examples=["Emirates Stadium", "Santiago Bernabeu"],
    )
    date: dt_date
    status: Status

    @field_validator("venue")
    @classmethod
    def normalize_venue(cls, value):
        if value is not None:
            return value.strip().lower()
        return value

    @model_validator(mode="after")
    def validate_date(self):
        if self.status == Status.upcoming and self.date < dt_date.today():
            raise ValueError("Upcoming match cannot be in the past")
        return self

    class Config:
        from_attributes = True


class MatchResponse(Match):
    id: int
    season: SeasonResponsewoLeague
    participants: list[MatchParticipantResponseforMatch] = Field(default_factory=list)

    @field_validator("venue")
    @classmethod
    def normalize_venue(cls, value):
        if value is not None:
            return value.strip().title()
        return value


class MatchFilters(BaseModel):

    season_id: Optional[int] = None
    venue: Optional[str] = None
    date: Optional[dt_date] = None
    status: Optional[Status] = None


class MatchUpdate(BaseModel):
    # Model for partial updates to a match. All fields are optional.

    venue: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100,
        examples=["Wembley Stadium"],
    )
    date: Optional[dt_date] = None
    status: Optional[Status] = Field(None, examples=["completed"])

    @field_validator("venue")
    @classmethod
    def format_venue(cls, value):
        if value is not None:
            return value.strip().lower()
        return value


class MatchListResponse(BaseModel):
    total: int
    page: int
    limit: int
    matches: List[MatchResponse]


class MatchDetails(BaseModel):
    season_id: int
    participants: List[MatchParticipantLite]

    class Config:
        from_attributes = True





class ParticipantInput(BaseModel):
    team_id: int = Field(gt=0)
    is_home: bool
    score: Optional[int] = Field(default=None, ge=0)  # None if match not completed yet


class MatchCreate(BaseModel):
    season_id: int
    venue: Optional[str] = Field(None, min_length=3, max_length=100)
    date: dt_date
    status: Status
    participants: List[ParticipantInput] = Field(min_length=2, max_length=2)

    @field_validator("venue")
    @classmethod
    def normalize_venue(cls, value):
        if value is not None:
            return value.strip().lower()
        return value

    @model_validator(mode="after")
    def validate_match(self):
        if self.status == Status.upcoming and self.date < dt_date.today():
            raise ValueError("Upcoming match cannot be in the past")

        # Validate exactly one home, one away
        home_count = sum(1 for p in self.participants if p.is_home)
        if home_count != 1:
            raise ValueError("Match must have exactly one home team and one away team")

        # Validate no duplicate teams
        team_ids = [p.team_id for p in self.participants]
        if len(set(team_ids)) != 2:
            raise ValueError("Both participants must be different teams")

        return self

    class Config:
        from_attributes = True


