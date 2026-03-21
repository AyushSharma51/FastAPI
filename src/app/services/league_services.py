from fastapi import HTTPException, status
from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from ..schemas.league_schemas import LeagueCreate

from ..db_models import League as LeagueModel, Season

#------------------------------------GET ALL LEAGUES--------------------------------------------------------

def get_all_leagues(db: Session):
    query = select(LeagueModel).where(LeagueModel.is_deleted.is_(False))
    teams = db.execute(query).scalars().all()
    return teams

#-------------------------------------CREATE A LEAGUE--------------------------------------------------------

def create_league(db: Session, league: LeagueCreate):
    """Create a new league"""
    league = LeagueModel(**league.model_dump())
    db.add(league)
    db.commit()
    db.refresh(league)
    return league

#--------------------------------------UPDATE A LEAGUE------------------------------------------------------------

def league_update(db, league_id, league):
    db_league = db.get(LeagueModel, league_id)
    if db_league is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="League not found"
        )

    # Only the fields the client explicitly sent
    update_data = league.model_dump(exclude_unset=True)

    if "name" in update_data:
        db_league.name = update_data["name"]

    db.commit()
    db.refresh(db_league)
    return db_league

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