from datetime import date as dt_date
from enum import Enum
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, computed_field, field_validator, model_validator


class Sport(str, Enum):
    football = "football"
    cricket = "cricket"
    hockey = "hockey"
    basketball = "basketball"
    baseball = "baseball"


class Status(str, Enum):
    upcoming = "upcoming"
    cancelled = "cancelled"
    abandoned = "abandoned"
    completed = "completed"


class Winner(str, Enum):
    home_team = "home_team"
    away_team = "away_team"
    draw = "draw"


class TeamFilter(str, Enum):
    won = "won"
    lost = "lost"
    draw = "draw"


class Player(BaseModel):
    number: int = Field(ge=1, le=99, description="Jersey number", examples=[10])
    name: str = Field(min_length=2, max_length=50, examples=["Lionel Messi"])
    position: Literal["goalkeeper", "defender", "midfielder", "forward"] = Field(
        examples=["forward"]
    )
    is_captain: bool = Field(default=False, examples=[True])


class Match(BaseModel):
    id: Optional[int] = None
    home_team_id: int
    away_team_id: int
    venue: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100,
        examples=["Emirates Stadium", "Santiago Bernabeu"],
    )
    date: dt_date
    sport: Sport
    status: Status
    is_draw: bool = False
    winner_id: Optional[int] = Field(
        None, title="Winner Team ID", description="Filter matches by winner team ID"
    )

    @field_validator("venue")
    @classmethod
    def normalize_venue(cls, value):
        if value is not None:
            return value.strip().lower()
        return value

    @model_validator(mode="after")
    def validate_match_logic(self):
        if self.home_team_id == self.away_team_id:
            raise ValueError("home_team and away_team must be different")
        if self.status == Status.completed:
            if self.winner_id is None:
                raise ValueError("Completed matches must have a winner")
        if self.status != Status.completed and self.winner_id is not None:
            raise ValueError("Only completed matches can have a winner")
        if self.status is Status.upcoming and self.date < dt_date.today():
            raise ValueError("Upcoming match date cannot be in the past")

        return self
    
    @model_validator(mode="after")
    def validate_draw_logic(self):

        if self.is_draw and self.winner_id is not None:
            raise ValueError("Draw match cannot have a winner")

        if self.is_draw and self.status != "finished":
            raise ValueError("Match must be finished to declare a draw")

        return self


class MatchUpdate(BaseModel):
    """Model for partial updates to a match. All fields are optional."""

    venue: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100,
        examples=["Wembley Stadium"],
    )
    date: Optional[dt_date] = None
    status: Optional[Status] = Field(None, examples=["completed"])
    is_draw: bool = False
    Field(None, title="Winner Team ID", description="Filter matches by winner team ID")
    winner_id: Optional[int]= None


    @field_validator("venue")
    @classmethod
    def normalize_venue(cls, value):
        if value is not None:
            return value.strip().lower()
        return value

    @model_validator(mode="after")
    def validate_update_logic(self):
        if self.status == Status.completed and self.winner_id is None:
            raise ValueError(
                "Cannot set status to completed without providing a winner"
            )
        if self.status != Status.completed and self.winner_id is not None:
            raise ValueError("Cannot set winner for non-completed matches")
        return self
    
    @model_validator(mode="after")
    def validate_draw_logic(self):

        if self.is_draw and self.winner_id is not None:
            raise ValueError("Draw match cannot have a winner")

        if self.is_draw and self.status != "finished":
            raise ValueError("Match must be finished to declare a draw")

        return self


class TeamResponse(BaseModel):
    id: int
    name: str


class MatchResponse(BaseModel):
    id: int
    home_team: TeamResponse
    away_team: TeamResponse
    venue: Optional[str] = None
    date: dt_date
    sport: Sport
    status: Status
    is_draw: bool = False
    winner_id: Optional[int] = None


class MatchListResponse(BaseModel):
    total: int
    page: int
    limit: int
    matches: List[MatchResponse]


class MatchFilters(BaseModel):
    sport: Optional[Sport] = Field(
        None,
        title="Sport Type",
        description="Filter matches by sport",
    )
    status: Optional[Status] = Field(
        None,
        title="Match Status",
        description="Filter by match status",
    )
    is_draw: bool = False
    winner_id: Optional[int] = Field(
        None, title="Winner Team ID", description="Filter matches by winner team ID"
    )

    team: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        pattern="^[A-Za-z0-9 ]+$",
        title="Team Name",
        description="Filter by team name. Case-insensitive partial match. Letters, numbers and spaces only.",
        examples=["Arsenal"],
    )
    team_filter: Optional[TeamFilter] = Field(
        None,
        title="Team Result Filter",
        description="Filter by how the team performed — won, lost, or draw. Requires team to be set.",
    )

    @model_validator(mode="after")
    def validate_winner_and_team_filter(self):
        if self.team_filter and self.winner_id:
            raise ValueError("team_filter and winner cannot be used together")
        if (self.team_filter or self.winner_id) and self.status not in (
            Status.completed,
            None,
        ):
            raise ValueError(
                "team_filter and winner can only be used when status is 'completed'"
            )
        return self

    @field_validator("team")
    @classmethod
    def normalize_team(cls, value):
        if value is not None:
            return value.strip()
        return value
    
    @model_validator(mode="after")
    def validate_draw_logic(self):

        if self.is_draw and self.winner_id is not None:
            raise ValueError("Draw match cannot have a winner")

        if self.is_draw and self.status != "finished":
            raise ValueError("Match must be finished to declare a draw")

        return self


class DateRangeFilters(BaseModel):
    from_date: Optional[dt_date] = Field(
        None,
        title="Start Date",
        description="Filter matches on or after this date (YYYY-MM-DD)",
        examples=["2026-01-01"],
    )
    to_date: Optional[dt_date] = Field(
        None,
        title="End Date",
        description="Filter matches on or before this date (YYYY-MM-DD)",
        examples=["2026-12-31"],
    )

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.from_date and self.to_date:
            if self.from_date > self.to_date:
                raise ValueError("from_date must be before or equal to to_date")
        return self


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    limit: int = Field(20, ge=1, le=100, description="Items per page (max 100)")

    @computed_field
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


class SortParams(BaseModel):
    sort_by: Optional[Literal["date", "sport", "status"]] = Field(
        None,
        title="Sort By",
        description="Field to sort results by",
    )
    sort_order: Literal["asc", "desc"] = Field(
        "asc",
        title="Sort Order",
        description="Sort direction — asc for ascending, desc for descending",
    )
