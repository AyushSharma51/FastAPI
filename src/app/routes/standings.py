"""
standings.py  –  FastAPI router for league standings (ASYNC VERSION).

Mount in main.py:
    from .routes.standings import router as standings_router
    app.include_router(standings_router)
"""

from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..schemas.standings_schemas import StandingsResponse
from ..services.standings_services import StandingsFilters, get_standings

router = APIRouter(prefix="/standings", tags=["Standings"])


# ---------------------- FILTER BUILDER ----------------------

def standings_filters(
    league_id: Optional[int] = Query(
        default=None,
        description="Filter standings to a specific league (returns all its seasons).",
        ge=1,
    ),
    season_id: Optional[int] = Query(
        default=None,
        description="Filter standings to a single season.",
        ge=1,
    ),
    sort_by: str = Query(
        default="points",
        description=(
            "Column to sort by. "
            "Allowed: points | wins | draws | losses | goal_difference | goals_for | played"
        ),
        pattern="^(points|wins|draws|losses|goal_difference|goals_for|played)$",
    ),
    sort_order: str = Query(
        default="desc",
        description="Sort direction: asc | desc",
        pattern="^(asc|desc)$",
    ),
) -> StandingsFilters:
    return StandingsFilters(
        league_id=league_id,
        season_id=season_id,
        sort_by=sort_by,
        sort_order=sort_order,
    )


# ---------------------------------------------------------------------------
# GET /standings
# ---------------------------------------------------------------------------

@router.get(
    "",
    response_model=List[StandingsResponse],
    status_code=status.HTTP_200_OK,
    summary="Get league standings",
    description="""
Returns standings grouped by season, calculated live from completed match data.

**Points system:** Win = 3 pts · Draw = 1 pt · Loss = 0 pts

**Filtering options**
- `league_id` — restrict to all seasons of a league
- `season_id` — restrict to a single season

**Sorting**
- `sort_by`: `points` (default), `wins`, `draws`, `losses`, `goal_difference`, `goals_for`, `played`
- `sort_order`: `desc` (default) or `asc`

Only matches with scores recorded for both teams are counted.
    """,
)
async def list_standings(
    filters: Annotated[StandingsFilters, Depends(standings_filters)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> List[StandingsResponse]:
    """
    Fetch league standings with filters and sorting.
    """
    return await get_standings(db, filters)