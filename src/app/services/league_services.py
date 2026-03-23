from sqlite3 import IntegrityError

from fastapi import HTTPException, status
from sqlalchemy import exists, select
from sqlalchemy.orm import Session

# from ..schemas.league_schemas import LeagueCreate

from ..db_models import League as LeagueModel, Season

#------------------------------------GET ALL LEAGUES--------------------------------------------------------

def get_all_leagues(db: Session):
    query = select(LeagueModel).where(LeagueModel.is_deleted.is_(False))
    teams = db.execute(query).scalars().all()
    return teams

#-------------------------------------CREATE A LEAGUE--------------------------------------------------------

def create_league(db, league):
    obj = LeagueModel(**league.model_dump())
    db.add(obj)

    try:
        db.flush()   # 🔥 IMPORTANT (catches early)
        db.commit()
        db.refresh(obj)
        return obj

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="name already exists"
        )

#--------------------------------------UPDATE A LEAGUE------------------------------------------------------------

def league_update(db, league_id, league):
    db_league = db.get(LeagueModel, league_id)

    if not db_league:
        raise HTTPException(404, "League not found")

    update_data = league.model_dump(exclude_unset=True)

    if "name" in update_data:
        db_league.name = update_data["name"]

    try:
        db.flush()   # 🔥 IMPORTANT
        db.commit()
        db.refresh(db_league)
        return db_league

    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "name already exists")
    
#---------------------------------------DELETE A LEAGUE----------------------------------------------------------

def delete_league(db: Session, league_id: int):
    league = db.get(LeagueModel, league_id)

    if not league:
        raise HTTPException(status_code=404, detail="League not found")

    #  Check if child exists
    has_seasons = db.query(
        exists().where(Season.league_id == league_id)
    ).scalar()

    if has_seasons:
        #  Soft delete
        league.is_deleted = True
        db.commit()
        return {"message": "League soft deleted (has seasons)"}

    else:
        #  Hard delete
        db.delete(league)
        db.commit()
        return {"message": "League permanently deleted"}