from typing import List

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from ..db_models import Match as MatchModel
from ..db_models import MatchParticipant as MatchParticipantModel
from ..db_models import Season as SeasonModel
from ..db_models import Team as TeamModel
from ..schemas.match_schemas import MatchCreate


def create_a_new_match(db: Session, matches: List[MatchCreate]):
    results=[]
    for match in matches:

        season = db.get(SeasonModel, match.season_id)
        if not season:
            raise HTTPException(404, "Season not found")

        if len(match.participants) != 2:
            raise HTTPException(400, "Match must have exactly 2 participants")

        team_ids = set()

        for p in match.participants:
            team = db.get(TeamModel, p.team_id)
            if not team:
                raise HTTPException(404, "Team not found")

            if p.team_id in team_ids:
                raise HTTPException(400, "Duplicate teams not allowed")

            team_ids.add(p.team_id)

        # Create the match — exclude participants, they're not a MatchModel field
        db_match = MatchModel(**match.model_dump(exclude={"participants"}))
        db.add(db_match)
        db.flush()  # flush so db_match.id is available for participants foriegn key, but don't commit yet

        # Create participants linked to the new match
        if len(match.participants) != 2:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Two teams are required")
        for p in match.participants:
            db_participant = MatchParticipantModel(
                match_id=db_match.id,
                team_id=p.team_id,
                is_home=p.is_home,
           
            )
            db.add(db_participant)

        db.commit()

        # Refresh with relationships loaded for the response
        db.refresh(db_match)
        results.append(db_match)
    return results


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
    else:
        query = query.order_by(MatchModel.id)

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

    db_match.venue = match.venue
    db_match.date = match.date
    db_match.status = match.status.value

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
