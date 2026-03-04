from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from typing import Annotated
from datetime import date as dt_date
from ..examples.match_examples import CREATE_MATCH_EXAMPLES, PATCH_MATCH_EXAMPLES, PUT_MATCH_EXAMPLES

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
    Status,
    TeamFilter,
    Winner,
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


@router.get(
    "/{match_id}",
    response_model=MatchResponse,
    response_model_exclude_none=True,
)
def get_match(match_id: Annotated[int, Path(ge=1, title="Match ID")]):
    for match in INITIAL_DATA:
        if match.id == match_id:
            return match
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")


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
    if match.status is Status.upcoming and match.date < dt_date.today():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Upcoming match date cannot be in the past",
        )
    match.id = INITIAL_DATA[-1].id + 1
    INITIAL_DATA.append(match)
    return match


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


@router.put(
    "/{match_id}",
    response_model=MatchResponse,
    response_model_exclude_none=True,
)
def replace_match(
    match_id: Annotated[int, Path(ge=1, title="Match ID")],
    match: Annotated[
        Match,
        Body(
            openapi_examples=PUT_MATCH_EXAMPLES
        ),
    ],
):
    for i, existing_match in enumerate(INITIAL_DATA):
        if existing_match.id == match_id:
            match.id = match_id
            INITIAL_DATA[i] = match
            return match

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")


@router.delete(
    "/{match_id}",
    response_model=MatchResponse,
    response_model_exclude_none=True,
)
def delete_match(match_id: Annotated[int, Path(ge=1, title="Match ID")]):
    for i, match in enumerate(INITIAL_DATA):
        if match.id == match_id:
            deleted_match = INITIAL_DATA.pop(i)
            return deleted_match

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
