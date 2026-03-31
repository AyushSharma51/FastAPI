from typing import Annotated, List

from fastapi import APIRouter, Body, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..examples.match_examples import (
    CREATE_MATCH_EXAMPLES,
    PATCH_MATCH_EXAMPLES,
    PUT_MATCH_EXAMPLES,
)
from ..schemas.common_schemas import DateRangeFilters, PaginationParams, SortParams
from ..schemas.match_schemas import (
    Match,
    MatchCreate,
    MatchFilters,
    MatchListResponse,
    MatchResponse,
    MatchUpdate,
)
from ..schemas.player_schemas import (
    PlayerMatchStatsCreate,
    PlayerMatchStatsResponse,
)
from ..services.match_services import (
    create_a_new_match,
    delete_a_match,
    get_all_matches,
    get_match_by_id,
    replace_a_match,
    update_a_match,
)
from ..services.player_services import (
    create_player_stats,
    list_player_stats,
    get_player_stat_by_id,
)
from ..security.deps import RoleChecker
from ..db_models import Role

router = APIRouter(prefix="/matches", tags=["Matches"])

allow_admin = RoleChecker([Role.ADMIN])
allow_admin_or_editor = RoleChecker([Role.ADMIN, Role.EDITOR])


# ================== PLAYER STATS ==================

@router.post(
    "/match-stats",
    response_model=PlayerMatchStatsResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(allow_admin_or_editor)],
)
async def create_new_player_stats(
    player_stats: PlayerMatchStatsCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Create player match statistics.

    Requires:
    - ADMIN or EDITOR role
    """
    return await create_player_stats(db, player_stats)


@router.get("/match-stats")
async def list_match_player_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends()],
):
    """
    Get paginated list of player match statistics.
    """
    return await list_player_stats(db, pagination)


@router.get(
    "/match-stats/{stat_id}",
    response_model=PlayerMatchStatsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_match_player_stat(
    stat_id: Annotated[int, Path(ge=1, title="Stat ID")],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get a specific player match stat by ID.
    """
    return await get_player_stat_by_id(db, stat_id)


# ================== GET (LIST) ==================

@router.get(
    "",
    response_model=MatchListResponse,
    response_model_exclude_none=True,
)
async def list_matches(
    filters: Annotated[MatchFilters, Depends()],
    date_range: Annotated[DateRangeFilters, Depends()],
    pagination: Annotated[PaginationParams, Depends()],
    sort_params: Annotated[SortParams, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get list of matches with filtering, sorting, and pagination.
    """
    return await get_all_matches(db, filters, date_range, sort_params, pagination)


# ================== GET (SINGLE) ==================

@router.get(
    "/{match_id}",
    response_model=MatchResponse,
    response_model_exclude_none=True,
)
async def get_match(
    match_id: Annotated[int, Path(ge=1, title="Match ID")],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get match details by ID.
    """
    return await get_match_by_id(db, match_id)


# ================== POST (CREATE) ==================

@router.post(
    "",
    response_model=List[MatchResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(allow_admin_or_editor)],
)
async def create_match(
    matches: Annotated[List[MatchCreate], Body(openapi_examples=CREATE_MATCH_EXAMPLES)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Create one or multiple matches.

    Requires:
    - ADMIN or EDITOR role
    """
    return await create_a_new_match(db, matches)


# ================== PATCH (UPDATE) ==================

@router.patch(
    "/{match_id}",
    response_model=MatchResponse,
    response_model_exclude_none=True,
    dependencies=[Depends(allow_admin_or_editor)],
)
async def update_match(
    match_id: Annotated[int, Path(ge=1, title="Match ID")],
    update: Annotated[MatchUpdate, Body(openapi_examples=PATCH_MATCH_EXAMPLES)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Partially update a match.

    Requires:
    - ADMIN or EDITOR role
    """
    return await update_a_match(db, match_id, update)


# ================== PUT (REPLACE) ==================

@router.put(
    "/{match_id}",
    response_model=MatchResponse,
    response_model_exclude_none=True,
    dependencies=[Depends(allow_admin_or_editor)],
)
async def replace_match(
    match_id: Annotated[int, Path(ge=1, title="Match ID")],
    match: Annotated[Match, Body(openapi_examples=PUT_MATCH_EXAMPLES)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Replace an entire match record.

    Requires:
    - ADMIN or EDITOR role
    """
    return await replace_a_match(db, match_id, match)


# ================== DELETE ==================

@router.delete(
    "/{match_id}",
    response_model=MatchResponse,
    response_model_exclude_none=True,
    dependencies=[Depends(allow_admin_or_editor)],
)
async def delete_match(
    match_id: Annotated[int, Path(ge=1, title="Match ID")],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Delete a match.

    Requires:
    - ADMIN or EDITOR role
    """
    return await delete_a_match(db, match_id)