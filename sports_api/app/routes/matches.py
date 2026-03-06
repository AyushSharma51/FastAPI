from fastapi import APIRouter, Body, Depends, Path, status
from typing import Annotated

from ..examples.match_examples import (
    CREATE_MATCH_EXAMPLES,
    PATCH_MATCH_EXAMPLES,
    PUT_MATCH_EXAMPLES,
)
from ..services.service import (
    get_all_matches,
    get_match_by_id,
    create_a_new_match,
    update_a_match,
    replace_a_match, 
    delete_a_match
)
from ..database import INITIAL_DATA

from ..schema import (
    DateRangeFilters,
    Match,
    MatchFilters,
    MatchListResponse,
    MatchResponse,
    MatchUpdate,
    PaginationParams,
    SortParams,
)

router = APIRouter(prefix="/matches", tags=["Matches"])


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
):
    return get_all_matches(INITIAL_DATA, filters, date_range, sort_params, pagination)


@router.get(
    "/{match_id}",
    response_model=MatchResponse,
    response_model_exclude_none=True,
)
def get_match(match_id: Annotated[int, Path(ge=1, title="Match ID")]):
    return get_match_by_id(INITIAL_DATA, match_id)


@router.post(
    "",
    response_model=MatchResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
def create_match(
    match: Annotated[
        Match,
        Body(openapi_examples=CREATE_MATCH_EXAMPLES),
    ],
):
    return create_a_new_match(INITIAL_DATA, match)


@router.patch(
    "/{match_id}",
    response_model=MatchResponse,
    response_model_exclude_none=True,
)
def update_match(
    match_id: Annotated[int, Path(ge=1, title="Match ID")],
    update: Annotated[
        MatchUpdate,
        Body(openapi_examples=PATCH_MATCH_EXAMPLES),
    ],
):
    return update_a_match(INITIAL_DATA, match_id, update)


@router.put(
    "/{match_id}",
    response_model=MatchResponse,
    response_model_exclude_none=True,
)
def replace_match(
    match_id: Annotated[int, Path(ge=1, title="Match ID")],
    match: Annotated[
        Match,
        Body(openapi_examples=PUT_MATCH_EXAMPLES),
    ],
):
    return replace_a_match(INITIAL_DATA,match_id,match)

@router.delete(
    "/{match_id}",
    response_model=MatchResponse,
    response_model_exclude_none=True,
)
def delete_match(match_id: Annotated[int, Path(ge=1, title="Match ID")]):
    return delete_a_match(INITIAL_DATA,match_id)

