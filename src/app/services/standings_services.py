from typing import Optional

# ---------------------------------------------------------------------------
# Filters schema (used by the route via Depends)
# ---------------------------------------------------------------------------
from pydantic import BaseModel
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from ..db_models import League, Match, MatchParticipant, Season, Team
from ..schemas.standings_schemas import StandingsResponse, TeamStandingEntry


class StandingsFilters(BaseModel):
    """Query-parameter filters for standings."""

    league_id: Optional[int] = None
    season_id: Optional[int] = None
    sort_by: str = (
        "points"  # points | wins | draws | losses | goal_difference | goals_for
    )
    sort_order: str = "desc"  # asc | desc

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Core service
# ---------------------------------------------------------------------------


def get_standings(
    db: Session,
    filters: StandingsFilters,
) -> list[StandingsResponse]:
    """
    Return standings grouped by season.  If season_id is supplied only that
    season is returned; if league_id is supplied all seasons for that league
    are returned; otherwise every season in the database is covered.
    """

    # ------------------------------------------------------------------
    # Step 1 – build a self-join on match_participants so each row has
    #          both the team's own score and the opponent's score.
    # ------------------------------------------------------------------
    mp_self = MatchParticipant.__table__.alias("mp_self")
    mp_opp = MatchParticipant.__table__.alias("mp_opp")

    # Raw aggregate CTE per (season, team)
    agg = (
        db.query(
            Match.season_id.label("season_id"),
            mp_self.c.team_id.label("team_id"),
            func.count().label("played"),
            func.sum(case((mp_self.c.score > mp_opp.c.score, 1), else_=0)).label(
                "wins"
            ),
            func.sum(case((mp_self.c.score == mp_opp.c.score, 1), else_=0)).label(
                "draws"
            ),
            func.sum(case((mp_self.c.score < mp_opp.c.score, 1), else_=0)).label(
                "losses"
            ),
            func.sum(mp_self.c.score).label("goals_for"),
            func.sum(mp_opp.c.score).label("goals_against"),
        )
        .select_from(mp_self)
        # join to the same match via the opponent row
        .join(
            mp_opp,
            (mp_self.c.match_id == mp_opp.c.match_id)
            & (mp_self.c.team_id != mp_opp.c.team_id),
        )
        # join to Match for season_id
        .join(Match, Match.id == mp_self.c.match_id)
        # only count completed matches (both scores present)
        .filter(mp_self.c.score.isnot(None))
        .filter(mp_opp.c.score.isnot(None))
        .group_by(Match.season_id, mp_self.c.team_id)
        .subquery()
    )

    # ------------------------------------------------------------------
    # Step 2 – join agg → Team, Season, League for readable names
    # ------------------------------------------------------------------
    rows = (
        db.query(
            agg.c.season_id,
            agg.c.team_id,
            Team.name.label("team_name"),
            Season.league_id.label("league_id"),
            League.name.label("league_name"),
            agg.c.played,
            agg.c.wins,
            agg.c.draws,
            agg.c.losses,
            agg.c.goals_for,
            agg.c.goals_against,
        )
        .join(Team, Team.id == agg.c.team_id)
        .join(Season, Season.id == agg.c.season_id)
        .join(League, League.id == Season.league_id)
    )

    # ------------------------------------------------------------------
    # Step 3 – apply filters
    # ------------------------------------------------------------------
    if filters.season_id:
        rows = rows.filter(agg.c.season_id == filters.season_id)
    if filters.league_id:
        rows = rows.filter(Season.league_id == filters.league_id)

    # Materialise before Python-side filtering (points / goal_diff not in SQL)
    raw = rows.all()

    # ------------------------------------------------------------------
    # Step 4 – build entry objects (computed_field kicks in here)
    # ------------------------------------------------------------------
    entries: list[TeamStandingEntry] = [
        TeamStandingEntry(
            team_id=r.team_id,
            team_name=r.team_name,
            season_id=r.season_id,
            league_id=r.league_id,
            league_name=r.league_name,
            played=r.played,
            wins=r.wins,
            draws=r.draws,
            losses=r.losses,
            goals_for=r.goals_for,
            goals_against=r.goals_against,
        )
        for r in raw
    ]

    # ------------------------------------------------------------------
    # Step 5 – sort
    # ------------------------------------------------------------------
    SORT_KEY_MAP = {
        "points": lambda e: e.points,
        "wins": lambda e: e.wins,
        "draws": lambda e: e.draws,
        "losses": lambda e: e.losses,
        "goal_difference": lambda e: e.goal_difference,
        "goals_for": lambda e: e.goals_for,
        "played": lambda e: e.played,
    }
    sort_key = SORT_KEY_MAP.get(filters.sort_by, lambda e: e.points)
    reverse = filters.sort_order.lower() != "asc"
    entries.sort(key=sort_key, reverse=reverse)

    # ------------------------------------------------------------------
    # Step 7 – group into per-season StandingsResponse objects
    # ------------------------------------------------------------------
    season_map: dict[int, list[TeamStandingEntry]] = {}
    for entry in entries:
        season_map.setdefault(entry.season_id, []).append(entry)

    responses: list[StandingsResponse] = []
    for season_id, season_entries in season_map.items():
        first = season_entries[0]
        responses.append(
            StandingsResponse(
                season_id=season_id,
                league_id=first.league_id,
                league_name=first.league_name,
                total_teams=len(season_entries),
                standings=season_entries,
            )
        )

    return responses
