from sqlalchemy.orm import Session
from sqlalchemy import func, select
from ..db_models import MatchModel
from ..schema import Winner, TeamFilter, Match
from fastapi import HTTPException, status

#---------------------------------------------GET ALL MATCHES---------------------------------------------------------------

def get_all_matches(db, filters, date_range, sort_params, pagination):
    query = select(MatchModel)

    if filters.sport:
        query = query.where(MatchModel.sport == filters.sport.value)
    if filters.status:
        query = query.where(MatchModel.status == filters.status.value)

    if filters.winner:
        query = query.where(MatchModel.winner == filters.winner.value)
    if filters.team:
        query = query.where(
            (MatchModel.home_team.contains(filters.team))
            | (MatchModel.away_team.contains(filters.team))
        )
    if filters.team_filter and filters.team:
        if filters.team_filter == TeamFilter.won:
            query = query.where(
                (
                    (MatchModel.winner == Winner.home_team.value)
                    & (MatchModel.home_team.contains(filters.team))
                )
                | (
                    (MatchModel.winner == Winner.away_team.value)
                    & (MatchModel.away_team.contains(filters.team))
                )
            )
        elif filters.team_filter == TeamFilter.lost:
            query = query.where(
                (
                    (MatchModel.winner == Winner.away_team.value)
                    & (MatchModel.home_team.contains(filters.team))
                )
                | (
                    (MatchModel.winner == Winner.home_team.value)
                    & (MatchModel.away_team.contains(filters.team))
                )
            )
        elif filters.team_filter == TeamFilter.draw:
            query = query.where(
                (MatchModel.winner == Winner.draw.value)
                & (
                    (MatchModel.home_team.contains(filters.team))
                    | (MatchModel.away_team.contains(filters.team))
                )
            )

    # Date range
    if date_range.from_date:
        query = query.where(MatchModel.date >= date_range.from_date)
    if date_range.to_date:
        query = query.where(MatchModel.date <= date_range.to_date)

    total = db.execute(select(func.count()).select_from(query.subquery())).scalar()

    # Sorting
    if sort_params.sort_by:
        sort_col = getattr(MatchModel, sort_params.sort_by)
        if sort_params.sort_order == "desc":
            sort_col = sort_col.desc()
        query = query.order_by(sort_col)

    # Pagination — LIMIT and OFFSET
    query = query.offset(pagination.offset).limit(pagination.limit)

    # Execute — get back a list of MatchModel objects
    matches = db.execute(query).scalars().all()

    return {
        "total": total,
        "page": 0,
        "limit": 0,
        "matches": matches,
    }

#---------------------------------------------------GET MATCH BY ID---------------------------------------------------------------

def get_match_by_id(db, match_id):
    match = db.get(MatchModel, match_id)
    if match is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Match not found"
        )
    return match

#---------------------------------------------------CREATE A NEW MATCH-------------------------------------------------------------


def create_a_new_match(db: Session, match: Match):

    db_match = MatchModel(**match.model_dump())

    db.add(db_match)
    db.commit()
    db.refresh(db_match)

    return db_match

#-----------------------------------------------------UPDATE A MATCH---------------------------------------------------------------

def update_a_match(db, match_id, update):
    db_match = db.get(MatchModel, match_id)
    if db_match is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Match not found"
        )

    # Only the fields the client explicitly sent
    update_data = update.model_dump(exclude_unset=True)

    # Validate the merged result before writing — same business rules as before
    stored_as_dict = {
        "id": db_match.id,
        "home_team": db_match.home_team,
        "away_team": db_match.away_team,
        "venue": db_match.venue,
        "date": db_match.date,
        "sport": db_match.sport,
        "status": db_match.status,
        "winner": db_match.winner,
    }
    merged = {**stored_as_dict, **update_data}
    try:
        Match.model_validate(merged)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    # Apply updates to the database model's attributes
    for field, value in update_data.items():
        if hasattr(db_match, field):
            db_value = value.value if hasattr(value, "value") else value
            setattr(db_match, field, db_value)

    db.commit()
    db.refresh(db_match)
    return db_match

#------------------------------------------------REPLACE A MATCH---------------------------------------------------------------------

def replace_a_match(db, match_id, match):
    db_match = db.get(MatchModel, match_id)
    if db_match is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Match not found"
        )

    # Overwrite every field
    db_match.home_team = match.home_team
    db_match.away_team = match.away_team
    db_match.venue = match.venue
    db_match.date = match.date
    db_match.sport = match.sport.value
    db_match.status = match.status.value
    db_match.winner = match.winner.value if match.winner else None

    db.commit()
    db.refresh(db_match)
    return db_match

#--------------------------------------------------DELETE A MATCH--------------------------------------------------------------------------

def delete_a_match(db, match_id):
    db_match = db.get(MatchModel, match_id)
    if db_match is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Match not found"
        )

    db.delete(db_match)
    db.commit()
    return db_match
