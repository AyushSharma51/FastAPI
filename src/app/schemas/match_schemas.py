from datetime import date as dt_date
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from ..schemas.match_participants_schemas import MatchParticipantLite, MatchParticipantResponseforMatch
from ..schemas.season_schemas import SeasonResponsewoLeague


class Status(str, Enum):
    upcoming = "upcoming"
    cancelled = "cancelled"
    abandoned = "abandoned"
    completed = "completed"


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


class MatchCreate(Match):
    pass


class MatchResponse(Match):
    id: int
    season: SeasonResponsewoLeague
    participants: list[MatchParticipantResponseforMatch] = Field(default_factory=list)


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
    def normalize_venue(cls, value):
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