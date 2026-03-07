from fastapi import APIRouter, Body, Depends, Path, status
from typing import Annotated
from sqlalchemy.orm import Session

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
    delete_a_match,
)
from ..database import get_db

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

#--------------------------------------------ROUTES----------------------------------------------------------------------

router = APIRouter(prefix="/matches", tags=["Matches"])

#---------------------------------------------GET(LIST)--------------------------------------------------------------------

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

#------------------------------------------POST(CREATE)-------------------------------------------------------------------

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
    db: Annotated[Session, Depends(get_db)],
):
    return create_a_new_match(db, match)

#------------------------------------------PATCH(UPDATE)-----------------------------------------------------------------

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
    db: Annotated[Session, Depends(get_db)],
):
    return update_a_match(db, match_id, update)

#---------------------------------------------PUT(REPLACE)---------------------------------------------------------------

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
    db: Annotated[Session, Depends(get_db)],
):
    return replace_a_match(db, match_id, match)

#-------------------------------------------------(DELETE)------------------------------------------------------------------

@router.delete(
    "/{match_id}",
    response_model=MatchResponse,
    response_model_exclude_none=True,
)
def delete_match(
    match_id: Annotated[int, Path(ge=1, title="Match ID")],
    db: Annotated[Session, Depends(get_db)],
):
    return delete_a_match(db, match_id)
