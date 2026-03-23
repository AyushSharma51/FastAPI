from fastapi import HTTPException
from sqlalchemy import exists, select
from sqlalchemy.orm import Session, joinedload

from ..db_models import League as LeagueModel, Season, Match
from ..db_models import Season as SeasonModel
from ..schemas.season_schemas import SeasonCreate, SeasonUpdate

#--------------------------------------LIST------------------------------------------------------

def list_season(db: Session):
    query = select(SeasonModel).options(joinedload(SeasonModel.league))

    season = db.execute(query).scalars().all()
    return season

#-----------------------------------POST(CREATE)---------------------------------------------------

def create_season(db: Session, season: SeasonCreate):

    # Check league exists in DB
    league = db.execute(
        select(LeagueModel).where(LeagueModel.id == season.league_id)
    ).scalar_one_or_none()

    if not league:
        raise HTTPException(status_code=404, detail="League not found")

    #  Create season
    season = SeasonModel(**season.model_dump())

    db.add(season)
    db.commit()
    db.refresh(season)

    return season

#--------------------------------------PUT(REPLACE)---------------------------------------------------
def update_season(db: Session, season_id: int, season: SeasonCreate):
    db_season = db.get(Season, season_id)

    if not db_season:
        raise HTTPException(status_code=404, detail="Season not found")

    # overwrite all fields
    db_season.league_id = season.league_id
    db_season.country = season.country
    db_season.start_date = season.start_date
    db_season.end_date = season.end_date

    db.commit()
    db.refresh(db_season)
    return db_season

#-----------------------------------------PATCH(UPDATE)-----------------------------------------------

def patch_season(db: Session, season_id: int, season: SeasonUpdate):
    db_season = db.get(Season, season_id)

    if not db_season:
        raise HTTPException(status_code=404, detail="Season not found")

    update_data = season.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_season, key, value)

    db.commit()
    db.refresh(db_season)
    return db_season

#-------------------------------------------DELETE----------------------------------------------------

def delete_season(db: Session, season_id: int):
    season = db.get(Season, season_id)

    if not season:
        raise HTTPException(status_code=404, detail="Season not found")

    # Check if matches exist
    has_matches = db.query(
        exists().where(Match.season_id == season_id)
    ).scalar()

    if has_matches:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete season with existing matches"
        )

    #  Hard delete
    db.delete(season)
    db.commit()

    return {"message": "Season deleted successfully"}