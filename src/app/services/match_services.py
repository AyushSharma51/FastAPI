from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, select
from ..db_models import Match as MatchModel
from ..schemas.match_schemas import Match
from fastapi import HTTPException, status

# ---------------------------------------------GET ALL MATCHES---------------------------------------------------------------


def get_all_matches(db, filters, date_range, sort_params, pagination):
    query = select(MatchModel).options(
        joinedload(MatchModel.season)  # Add this to fix N+1 for winners
    )

    if filters.status:
        query = query.where(MatchModel.status == filters.status.value)

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


# ---------------------------------------------------GET MATCH BY ID---------------------------------------------------------------


def get_match_by_id(db, match_id):
    match = db.get(MatchModel, match_id)

    if match is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Match not found"
        )
    return match


# ---------------------------------------------------CREATE A NEW MATCH-------------------------------------------------------------


def create_a_new_match(db: Session, match: Match):

    db_match = MatchModel(**match.model_dump())

    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    # if db_match.status=completed
    return db_match


# -----------------------------------------------------UPDATE A MATCH---------------------------------------------------------------


def update_a_match(db, match_id, update):
    db_match = db.get(MatchModel, match_id)
    if db_match is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Match not found"
        )

    # Only the fields the client explicitly sent
    update_data = update.model_dump(exclude_unset=True)

    if "venue" in update_data:
        db_match.venue = update_data["venue"]
    if "date" in update_data:
        db_match.date = update_data["data"]
    if "status" in update_data:
        db_match.status = update_data["status"]
    # if "winner" in update_data:
    #     db_match.winner_id = update_data["winner_id"]
    # if "is_draw" in update_data:
    #     db_match.is_draw = update_data["is_draw"]
    #     if update_data["is_draw"]:
    #         db_match.winner_id = None

    db.commit()
    db.refresh(db_match)
    return db_match


# ------------------------------------------------REPLACE A MATCH---------------------------------------------------------------------


def replace_a_match(db, match_id, match):
    db_match = db.get(MatchModel, match_id)
    if db_match is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Match not found"
        )

    # # Overwrite every field
    # db_match.home_team_id = match.home_team_id
    # db_match.away_team_id = match.away_team_id
    db_match.venue = match.venue
    db_match.date = match.date
    # db_match.sport = match.sport.value
    db_match.status = match.status.value
    # db_match.is_draw = match.is_draw.value
    # db_match.winner_id = match.winner_id.value if match.winner_id else None

    db.commit()
    db.refresh(db_match)
    return db_match


# --------------------------------------------------DELETE A MATCH--------------------------------------------------------------------------


def delete_a_match(db, match_id):
    db_match = db.get(MatchModel, match_id)
    if db_match is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Match not found"
        )

    db.delete(db_match)
    db.commit()
    return db_match
