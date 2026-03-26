from typing import Annotated, List

from fastapi import APIRouter, Body, Depends, Path, status
from sqlalchemy.orm import Session

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


# ================== PLAYER STATS  ==================


@router.post(
    "/match-stats",
    response_model=PlayerMatchStatsResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(allow_admin_or_editor)],
)
def create_new_player_stats(
    player_stats: PlayerMatchStatsCreate,
    db: Annotated[Session, Depends(get_db)],
):
    return create_player_stats(db, player_stats)


@router.get("/match-stats")
def list_match_player_stats(
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends()],
):
    return list_player_stats(db, pagination)


@router.get(
    "/match-stats/{stat_id}",
    response_model=PlayerMatchStatsResponse,
    status_code=status.HTTP_200_OK,
)
def get_match_player_stat(
    stat_id: Annotated[int, Path(ge=1, title="Stat ID")],
    db: Annotated[Session, Depends(get_db)],
):
    return get_player_stat_by_id(db, stat_id)


# ================== GET (LIST) ==================


@router.get(
    "",
    response_model=MatchListResponse,
    response_model_exclude_none=True,
)
def list_matches(
    filters: Annotated[MatchFilters, Depends()],
    date_range: Annotated[DateRangeFilters, Depends()],
    pagination: Annotated[PaginationParams, Depends()],
    sort_params: Annotated[SortParams, Depends()],
    db: Annotated[Session, Depends(get_db)],
):
    return get_all_matches(db, filters, date_range, sort_params, pagination)


# ================== GET (SINGLE) ==================


@router.get(
    "/{match_id}",
    response_model=MatchResponse,
    response_model_exclude_none=True,
)
def get_match(
    match_id: Annotated[int, Path(ge=1, title="Match ID")],
    db: Annotated[Session, Depends(get_db)],
):
    return get_match_by_id(db, match_id)


# ================== POST (CREATE) ==================


@router.post(
    "",
    response_model=List[MatchResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(allow_admin_or_editor)],
)
def create_match(
    matches: Annotated[List[MatchCreate], Body(openapi_examples=CREATE_MATCH_EXAMPLES)],
    db: Annotated[Session, Depends(get_db)],
):
    return create_a_new_match(db, matches)


# ================== PATCH (UPDATE) ==================


@router.patch(
    "/{match_id}",
    response_model=MatchResponse,
    response_model_exclude_none=True,
    dependencies=[Depends(allow_admin_or_editor)],
)
def update_match(
    match_id: Annotated[int, Path(ge=1, title="Match ID")],
    update: Annotated[MatchUpdate, Body(openapi_examples=PATCH_MATCH_EXAMPLES)],
    db: Annotated[Session, Depends(get_db)],
):
    return update_a_match(db, match_id, update)


# ================== PUT (REPLACE) ==================


@router.put(
    "/{match_id}",
    response_model=MatchResponse,
    response_model_exclude_none=True,
    dependencies=[Depends(allow_admin_or_editor)],
)
def replace_match(
    match_id: Annotated[int, Path(ge=1, title="Match ID")],
    match: Annotated[Match, Body(openapi_examples=PUT_MATCH_EXAMPLES)],
    db: Annotated[Session, Depends(get_db)],
):
    return replace_a_match(db, match_id, match)


# ================== DELETE ==================


@router.delete(
    "/{match_id}",
    response_model=MatchResponse,
    response_model_exclude_none=True,
    dependencies=[Depends(allow_admin_or_editor)],
)
def delete_match(
    match_id: Annotated[int, Path(ge=1, title="Match ID")],
    db: Annotated[Session, Depends(get_db)],
):
    return delete_a_match(db, match_id)
