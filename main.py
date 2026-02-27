import math
from datetime import date
from enum import Enum
from operator import attrgetter
from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Sports Matches API")


# -------------------- ENUMS --------------------


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


class SortBy(str, Enum):
    date = "date"
    sport = "sport"
    status = "status"
    home_team = "home_team"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


# -------------------- MODELS --------------------


class Match(BaseModel):
    id: int
    home_team: str
    away_team: str
    venue: Optional[str] = None
    date: date
    sport: Sport
    status: Status
    winner: Optional[Winner] = None


# -------------------- DATA --------------------

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


class TeamFilter(str, Enum):
    won = "won"
    lost = "lost"
    draw = "draw"


# -------------------- ROUTES --------------------


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok"}


@app.get("/matches", tags=["Matches"])
def list_matches(
    status: Optional[Status] = None,
    sport: Optional[Sport] = None,
    winner: Optional[Winner] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    team_name: Optional[str] = None,
    team_filter: Optional[TeamFilter] = None,
    page: int = 1,
    limit: int = 10,
    sort_by: Optional[SortBy] = None,
    sort_order: SortOrder = SortOrder.asc,
):
    if team_filter and winner:
        return {"Error": "These team_filter and winner cannot be selected together."}
    if (team_filter or winner) and (
        status is not Status.completed and status is not None
    ):
        return {"Error": "team_filter or winner can only be used when status is 'completed'."}

    if start_date and end_date and start_date > end_date:
        return {"Error": "start_date must be before or equal to end_date."}

    matches = INITIAL_DATA

    if status:
        matches = [m for m in matches if m.status == status]
    if sport:
        matches = [m for m in matches if m.sport == sport]
    if winner:
        matches = [m for m in matches if m.winner == winner]
    if start_date:
        matches = [m for m in matches if m.date >= start_date]
    if end_date:
        matches = [m for m in matches if m.date <= end_date]

    if team_name:
        team = team_name.lower()
        if team_filter is None:
            matches = [m for m in matches if team in m.home_team.lower() or team in m.away_team.lower()]
        elif team_filter is TeamFilter.won:
            matches = [match for match in matches if
                       (team == match.home_team.lower() and match.winner == Winner.home_team) or
                       (team == match.away_team.lower() and match.winner == Winner.away_team)]
        elif team_filter is TeamFilter.lost:
            matches = [match for match in matches if
                       (team == match.home_team.lower() and match.winner != Winner.home_team) or
                       (team == match.away_team.lower() and match.winner != Winner.away_team)]
        elif team_filter is TeamFilter.draw:
            matches = [match for match in matches if
                       (team == match.home_team.lower() or team == match.away_team.lower()) and
                       match.winner == Winner.draw]

    if not matches:
        return {"message": "No matches found for the given filters."}

    if sort_by:
        reverse = sort_order == "desc"
        matches.sort(key=attrgetter(sort_by), reverse=reverse)

    total = len(matches)
    total_pages = math.ceil(total / limit)
    start = (page - 1) * limit
    end = start + limit
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "matches": matches[start:end],
    }


@app.get("/matches/{match_id}", tags=["Matches"])
def get_match_by_id(match_id: int):
    matches = INITIAL_DATA
    matches = [match for match in matches if match.id == match_id]
    if len(matches) == 0:
        return {"error": "Match Id not found"}
    return matches[0]


@app.post("/matches", tags=["Matches"])
def create_match(match: Match):
    if match.status is Status.upcoming:
        if match.date < date.today():
            return {"Error": "Upcoming match date cannot be in the past."}
    if match.status is not Status.completed:
        if match.winner is not None:
            return {"Error": "Status should be Completed to have a winner"}
    if match.home_team == match.away_team:
        return {"Error": "Both teams cannot have the same name."}
    if match.winner is None:
        if match.status is Status.completed:
            return {"Error": " Winner cannot be None if match is completed"}
    new_id = INITIAL_DATA[-1].id + 1
    match.id = new_id
    INITIAL_DATA.append(match)
    return match
