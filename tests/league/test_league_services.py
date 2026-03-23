from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from src.app.db_models import League as LeagueModel


# ---------------------- CREATE ----------------------

def create_league(db, league):
    obj = LeagueModel(**league.model_dump())
    db.add(obj)

    try:
        db.commit()
        db.refresh(obj)
        return obj

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="name already exists"
        )


# ---------------------- UPDATE ----------------------

def league_update(db, league_id, league):
    db_league = db.get(LeagueModel, league_id)

    if not db_league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found"
        )

    update_data = league.model_dump(exclude_unset=True)

    if "name" in update_data:
        db_league.name = update_data["name"]

    try:
        db.commit()
        db.refresh(db_league)
        return db_league

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="name already exists"
        )