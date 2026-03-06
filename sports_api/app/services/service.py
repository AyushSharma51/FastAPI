from ..schema import Winner, TeamFilter, Status, Match
from fastapi import HTTPException, status
from datetime import date as dt_date

def get_all_matches(INITIAL_DATA,filters,date_range, sort_params,pagination):
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

def get_match_by_id(INITIAL_DATA,match_id):
    for match in INITIAL_DATA:
        if match.id == match_id:
            return match
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")

def create_a_new_match(INITIAL_DATA,match):
    if match.status is Status.upcoming and match.date < dt_date.today():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Upcoming match date cannot be in the past",
        )
    match.id = INITIAL_DATA[-1].id + 1
    INITIAL_DATA.append(match)
    return match

def update_a_match(INITIAL_DATA,match_id,update):
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

def replace_a_match(INITIAL_DATA,match_id,match):
    for i, existing_match in enumerate(INITIAL_DATA):
        if existing_match.id == match_id:
            match.id = match_id
            INITIAL_DATA[i] = match
            return match

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")

def  delete_a_match(INITIAL_DATA,match_id):
    for i, match in enumerate(INITIAL_DATA):
        if match.id == match_id:
            deleted_match = INITIAL_DATA.pop(i)
            return deleted_match

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")

