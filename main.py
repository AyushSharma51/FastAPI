from datetime import date
from enum import Enum
from typing import Annotated, List, Literal, Optional

from fastapi import FastAPI, Query
from pydantic import BaseModel

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


class Match(BaseModel):
    id: int
    home_team: str
    away_team: str
    venue: Optional[str] = None
    date: date
    sport: Sport
    status: Status
    winner: Optional[Winner] = None


INITIAL_DATA: List[Match] = [
    Match(id=1, home_team="Arsenal", away_team="Chelsea", sport=Sport.football,
          date=date(2025, 10, 21), status=Status.completed, winner=Winner.draw,
          venue="Emirates Stadium"),
    Match(id=2, home_team="Lakers", away_team="Warriors", sport=Sport.basketball,
          date=date(2025, 11, 15), status=Status.completed, winner=Winner.home_team,
          venue="Crypto.com Arena"),
    Match(id=3, home_team="Real Madrid", away_team="Barcelona", sport=Sport.football,
          date=date(2026, 4, 10), status=Status.completed, winner=Winner.draw,
          venue="Santiago Bernabeu"),
    Match(id=4, home_team="Knicks", away_team="Celtics", sport=Sport.basketball,
          date=date(2026, 3, 5), status=Status.upcoming, winner=None,
          venue="Madison Square Garden"),
    Match(id=5, home_team="Yankees", away_team="Red Sox", sport=Sport.baseball,
          date=date(2025, 8, 10), status=Status.abandoned, winner=None,
          venue="Yankee Stadium"),
    Match(id=6, home_team="India", away_team="Pakistan", sport=Sport.cricket,
          date=date(2026, 3, 24), status=Status.completed, winner=Winner.home_team,
          venue="Narendra Modi Stadium"),
    Match(id=7, home_team="Lakers", away_team="Warriors", sport=Sport.basketball,
          date=date(2025, 1, 15), status=Status.completed, winner=Winner.away_team,
          venue="Crypto.com Arena"),
]


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok"}


@app.get("/matches", tags=["Matches"])
def list_matches(
    sport: Annotated[
        Optional[Sport],
        Query(title="Sport Type", description="Filter matches by sport"),
    ] = None,
    status: Annotated[
        Optional[Status],
        Query(title="Match Status", description="Filter by match status"),
    ] = None,
    winner: Annotated[Optional[Winner], Query()] = None,
    team_name: Annotated[
        Optional[str],
        Query(min_length=3, max_length=50, title="Team Name",
              description="Filter by team name. Case-insensitive partial match."),
    ] = None,
    team_filter: Annotated[Optional[TeamFilter], Query()] = None,
    from_date: Annotated[
        Optional[date],
        Query(alias="from-date", title="Start Date",
              description="Filter matches on or after this date (YYYY-MM-DD)"),
    ] = None,
    to_date: Annotated[
        Optional[date],
        Query(alias="to-date", title="End Date",
              description="Filter matches on or before this date (YYYY-MM-DD)"),
    ] = None,
    page: Annotated[int, Query(ge=1, description="Page number (1-indexed)")] = 1,
    limit: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 20,
    sort_by: Annotated[
        Optional[Literal["date", "sport", "status", "home_team"]],
        Query(description="Field to sort by"),
    ] = None,
    sort_order: Annotated[Literal["asc", "desc"], Query(description="Sort order")] = "asc",
):
    if from_date and to_date and from_date > to_date:
        return {"error": "from-date must be before to-date"}

    matches = list(INITIAL_DATA)

    if status:
        matches = [m for m in matches if m.status == status]
    if sport:
        matches = [m for m in matches if m.sport == sport]
    if winner:
        matches = [m for m in matches if m.winner == winner]
    if from_date:
        matches = [m for m in matches if m.date >= from_date]
    if to_date:
        matches = [m for m in matches if m.date <= to_date]

    if team_name:
        team = team_name.lower()
        if team_filter is None:
            matches = [m for m in matches if team in m.home_team.lower() or team in m.away_team.lower()]
        elif team_filter == TeamFilter.won:
            matches = [m for m in matches if
                       (team == m.home_team.lower() and m.winner == Winner.home_team) or
                       (team == m.away_team.lower() and m.winner == Winner.away_team)]
        elif team_filter == TeamFilter.lost:
            matches = [m for m in matches if
                       (team == m.home_team.lower() and m.winner == Winner.away_team) or
                       (team == m.away_team.lower() and m.winner == Winner.home_team)]
        elif team_filter == TeamFilter.draw:
            matches = [m for m in matches if
                       (team in m.home_team.lower() or team in m.away_team.lower()) and
                       m.winner == Winner.draw]

    if sort_by:
        matches = sorted(matches, key=lambda m: getattr(m, sort_by),
                         reverse=(sort_order == "desc"))

    total = len(matches)
    total_pages = (total + limit - 1) // limit if total > 0 else 0

    if page > total_pages and total > 0:
        return {"error": f"Page {page} does not exist. Total pages: {total_pages}",
                "total": total, "total_pages": total_pages}

    start = (page - 1) * limit
    paginated = matches[start:start + limit]

    if not paginated:
        return {"message": "No matches found.", "total": 0, "page": page,
                "limit": limit, "total_pages": 0, "results": []}

    return {"total": total, "page": page, "limit": limit,
            "total_pages": total_pages, "results": paginated}


@app.get("/matches/{match_id}", tags=["Matches"])
def get_match_by_id(match_id: int):
    for match in INITIAL_DATA:
        if match.id == match_id:
            return match
    return {"error": "Match not found"}


@app.post("/matches", tags=["Matches"])
def create_match(match: Match):
    if match.status is Status.upcoming and match.date < date.today():
        return {"error": "Upcoming match date cannot be in the past."}
    if match.status is not Status.completed and match.winner is not None:
        return {"error": "Status should be Completed to have a winner"}
    if match.home_team == match.away_team:
        return {"error": "Both teams cannot have the same name."}
    if match.winner is None and match.status is Status.completed:
        return {"error": "Winner cannot be None if match is completed"}
    match.id = INITIAL_DATA[-1].id + 1
    INITIAL_DATA.append(match)
    return match
