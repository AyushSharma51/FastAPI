from datetime import date as dt_date
from enum import Enum
from typing import Annotated, List, Literal, Optional

from fastapi import Body, Depends, FastAPI, HTTPException, Path, status
from pydantic import BaseModel, Field, computed_field, field_validator, model_validator

app = FastAPI(title="Sports Matches API")


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
    home_team: str = Field(
        min_length=2, max_length=50, examples=["Arsenal", "Real Madrid"]
    )
    away_team: str = Field(
        min_length=2, max_length=50, examples=["Chelsea", "Barcelona"]
    )
    venue: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100,
        examples=["Emirates Stadium", "Santiago Bernabeu"],
    )
    date: dt_date
    sport: Sport
    status: Status
    winner: Optional[Winner] = None
    home_lineup: Optional[List[Player]] = None
    away_lineup: Optional[List[Player]] = None

    @field_validator("home_team", "away_team")
    @classmethod
    def normalize_team_name(cls, value):
        return value.strip().lower()

    @field_validator("venue")
    @classmethod
    def normalize_venue(cls, value):
        if value is not None:
            return value.strip().lower()
        return value

    @model_validator(mode="after")
    def validate_match_logic(self):
        if self.home_team == self.away_team:
            raise ValueError("home_team and away_team must be different")
        if self.status == Status.completed:
            if self.winner is None:
                raise ValueError("Completed matches must have a winner")
        if self.status != Status.completed and self.winner is not None:
            raise ValueError("Only completed matches can have a winner")
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
    winner: Optional[Winner] = Field(None, examples=["home_team"])
    home_lineup: Optional[List[Player]] = None
    away_lineup: Optional[List[Player]] = None

    @field_validator("venue")
    @classmethod
    def normalize_venue(cls, value):
        if value is not None:
            return value.strip().lower()
        return value

    @model_validator(mode="after")
    def validate_update_logic(self):
        if self.status == Status.completed and self.winner is None:
            raise ValueError(
                "Cannot set status to completed without providing a winner"
            )
        if self.status != Status.completed and self.winner is not None:
            raise ValueError("Cannot set winner for non-completed matches")
        return self


class MatchResponse(BaseModel):
    id: int
    home_team: str
    away_team: str
    venue: Optional[str] = None
    date: dt_date
    sport: Sport
    status: Status
    winner: Optional[Winner] = None
    home_lineup: Optional[List[Player]] = None
    away_lineup: Optional[List[Player]] = None


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
    winner: Optional[Winner] = Field(
        None,
        title="Winner",
        description="Filter by match winner",
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
        if self.team_filter and self.winner:
            raise ValueError("team_filter and winner cannot be used together")
        if (self.team_filter or self.winner) and self.status not in (
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
            return value.strip().lower()
        return value


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


INITIAL_DATA: List[Match] = [
    Match(
        id=1,
        home_team="Arsenal",
        away_team="Chelsea",
        sport=Sport.football,
        date=dt_date(2025, 10, 21),
        status=Status.completed,
        winner=Winner.draw,
        venue="Emirates Stadium",
    ),
    Match(
        id=2,
        home_team="Lakers",
        away_team="Warriors",
        sport=Sport.basketball,
        date=dt_date(2025, 11, 15),
        status=Status.completed,
        winner=Winner.home_team,
        venue="Crypto.com Arena",
    ),
    Match(
        id=3,
        home_team="Real Madrid",
        away_team="Barcelona",
        sport=Sport.football,
        date=dt_date(2026, 4, 10),
        status=Status.completed,
        winner=Winner.draw,
        venue="Santiago Bernabeu",
    ),
    Match(
        id=4,
        home_team="Knicks",
        away_team="Celtics",
        sport=Sport.basketball,
        date=dt_date(2026, 3, 5),
        status=Status.upcoming,
        winner=None,
        venue="Madison Square Garden",
    ),
    Match(
        id=5,
        home_team="Yankees",
        away_team="Red Sox",
        sport=Sport.baseball,
        date=dt_date(2025, 8, 10),
        status=Status.abandoned,
        winner=None,
        venue="Yankee Stadium",
    ),
    Match(
        id=6,
        home_team="India",
        away_team="Pakistan",
        sport=Sport.cricket,
        date=dt_date(2026, 3, 24),
        status=Status.completed,
        winner=Winner.home_team,
        venue="Narendra Modi Stadium",
    ),
    Match(
        id=7,
        home_team="Lakers",
        away_team="Warriors",
        sport=Sport.basketball,
        date=dt_date(2025, 1, 15),
        status=Status.completed,
        winner=Winner.away_team,
        venue="Crypto.com Arena",
    ),
]


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


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok"}


@app.get("/matches", response_model=MatchListResponse, response_model_exclude_none=True, tags=["Matches"])
def list_matches(
    filters: Annotated[MatchFilters, Depends()],
    date_range: Annotated[DateRangeFilters, Depends()],
    pagination: Annotated[PaginationParams, Depends()],
    sort_params: Annotated[SortParams, Depends()],
):
    results = INITIAL_DATA

    if filters.sport:
        results = [m for m in results if m.sport == filters.sport]

    if filters.status:
        results = [m for m in results if m.status == filters.status]

    if filters.winner:
        results = [m for m in results if m.winner == filters.winner]

    if filters.team:
        normalized_team = filters.team.strip().lower()
        results = [
            m
            for m in results
            if normalized_team in m.home_team or normalized_team in m.away_team
        ]

    if filters.team_filter and filters.team:
        normalized_team = filters.team.strip().lower()
        if filters.team_filter == TeamFilter.won:
            results = [
                m
                for m in results
                if (m.winner == Winner.home_team and normalized_team in m.home_team)
                or (m.winner == Winner.away_team and normalized_team in m.away_team)
            ]
        elif filters.team_filter == TeamFilter.lost:
            results = [
                m
                for m in results
                if (m.winner == Winner.away_team and normalized_team in m.home_team)
                or (m.winner == Winner.home_team and normalized_team in m.away_team)
            ]
        elif filters.team_filter == TeamFilter.draw:
            results = [
                m
                for m in results
                if m.winner == Winner.draw
                and (normalized_team in m.home_team or normalized_team in m.away_team)
            ]

    if date_range.from_date:
        results = [m for m in results if m.date >= date_range.from_date]

    if date_range.to_date:
        results = [m for m in results if m.date <= date_range.to_date]

    if sort_params.sort_by:
        reverse = sort_params.sort_order == "desc"
        results = sorted(
            results, key=lambda m: getattr(m, sort_params.sort_by), reverse=reverse
        )

    total = len(results)
    results = results[pagination.offset : pagination.offset + pagination.limit]

    return {
        "total": total,
        "page": pagination.page,
        "limit": pagination.limit,
        "matches": results,
    }


@app.get("/matches/{match_id}", response_model=MatchResponse, response_model_exclude_none=True, tags=["Matches"])
def get_match(match_id: Annotated[int, Path(ge=1, title="Match ID")]):
    for match in INITIAL_DATA:
        if match.id == match_id:
            return match
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")


@app.post("/matches", response_model=MatchResponse, response_model_exclude_none=True, status_code=status.HTTP_201_CREATED, tags=["Matches"])
def create_match(
    match: Annotated[
        Match,
        Body(
            openapi_examples={
                "basic": {
                    "summary": "Basic upcoming match",
                    "description": "Minimal required fields for creating a new match",
                    "value": {
                        "home_team": "Arsenal",
                        "away_team": "Chelsea",
                        "sport": "football",
                        "date": "2026-03-15",
                        "status": "upcoming",
                        "venue": "Emirates Stadium",
                    },
                },
                "completed": {
                    "summary": "Completed match",
                    "description": "A finished match with a winner",
                    "value": {
                        "home_team": "Real Madrid",
                        "away_team": "Barcelona",
                        "sport": "football",
                        "date": "2025-10-26",
                        "status": "completed",
                        "venue": "Santiago Bernabeu",
                        "winner": "home_team",
                    },
                },
                "with_lineup": {
                    "summary": "Match with player lineup",
                    "description": "Include starting lineups for both teams",
                    "value": {
                        "home_team": "Arsenal",
                        "away_team": "Chelsea",
                        "sport": "football",
                        "date": "2026-03-15",
                        "status": "upcoming",
                        "venue": "Emirates Stadium",
                        "home_lineup": [
                            {
                                "number": 1,
                                "name": "Aaron Ramsdale",
                                "position": "goalkeeper",
                                "is_captain": False,
                            },
                            {
                                "number": 10,
                                "name": "Martin Odegaard",
                                "position": "midfielder",
                                "is_captain": True,
                            },
                        ],
                        "away_lineup": [
                            {
                                "number": 1,
                                "name": "Kepa Arrizabalaga",
                                "position": "goalkeeper",
                                "is_captain": False,
                            }
                        ],
                    },
                },
            }
        ),
    ],
):
    if match.status is Status.upcoming and match.date < dt_date.today():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Upcoming match date cannot be in the past",
        )
    match.id = INITIAL_DATA[-1].id + 1
    INITIAL_DATA.append(match)
    return match


@app.patch("/matches/{match_id}", response_model=MatchResponse, response_model_exclude_none=True, tags=["Matches"])
def update_match(
    match_id: Annotated[int, Path(ge=1, title="Match ID")],
    update: Annotated[
        MatchUpdate,
        Body(
            openapi_examples={
                "update_venue": {
                    "summary": "Update venue only",
                    "description": "Change the match venue without affecting other fields",
                    "value": {"venue": "Wembley Stadium"},
                },
                "record_result": {
                    "summary": "Record match result",
                    "description": "Update a match with completion status and winner",
                    "value": {
                        "status": "completed",
                        "winner": "home_team",
                    },
                },
                "reschedule_match": {
                    "summary": "Reschedule match date",
                    "description": "Change the date and venue for an upcoming match",
                    "value": {
                        "date": "2026-06-15",
                        "venue": "Etihad Stadium",
                    },
                },
                "add_lineup": {
                    "summary": "Add team lineup",
                    "description": "Add starting lineup before match",
                    "value": {
                        "home_lineup": [
                            {
                                "number": 1,
                                "name": "Aaron Ramsdale",
                                "position": "goalkeeper",
                                "is_captain": False,
                            },
                            {
                                "number": 10,
                                "name": "Martin Odegaard",
                                "position": "midfielder",
                                "is_captain": True,
                            },
                        ]
                    },
                },
            }
        ),
    ],
):
    for i, match in enumerate(INITIAL_DATA):
        if match.id == match_id:
            stored_match_data = match.model_dump()
            update_data = update.model_dump(exclude_unset=True)
            updated_match_dict = {**stored_match_data, **update_data}

            try:
                validated_match = Match.model_validate(updated_match_dict)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=str(e),
                )

            INITIAL_DATA[i] = validated_match
            return validated_match

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")


@app.put("/matches/{match_id}", response_model=MatchResponse, response_model_exclude_none=True, tags=["Matches"])
def replace_match(
    match_id: Annotated[int, Path(ge=1, title="Match ID")],
    match: Annotated[
        Match,
        Body(
            openapi_examples={
                "replace_upcoming": {
                    "summary": "Replace with upcoming match",
                    "description": "Completely replace match data with new upcoming match details",
                    "value": {
                        "home_team": "Manchester City",
                        "away_team": "Tottenham",
                        "sport": "football",
                        "date": "2026-05-20",
                        "status": "upcoming",
                        "venue": "Etihad Stadium",
                    },
                },
                "replace_completed": {
                    "summary": "Replace with completed match",
                    "description": "Replace entire match with completed match data including winner",
                    "value": {
                        "home_team": "Arsenal",
                        "away_team": "Chelsea",
                        "sport": "football",
                        "date": "2026-05-15",
                        "status": "completed",
                        "venue": "Wembley Stadium",
                        "winner": "home_team",
                    },
                },
            }
        ),
    ],
):
    for i, existing_match in enumerate(INITIAL_DATA):
        if existing_match.id == match_id:
            match.id = match_id
            INITIAL_DATA[i] = match
            return match

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")


@app.delete("/matches/{match_id}", response_model=MatchResponse, response_model_exclude_none=True, tags=["Matches"])
def delete_match(match_id: Annotated[int, Path(ge=1, title="Match ID")]):
    for i, match in enumerate(INITIAL_DATA):
        if match.id == match_id:
            deleted_match = INITIAL_DATA.pop(i)
            return deleted_match

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
