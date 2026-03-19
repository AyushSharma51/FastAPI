from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..db_models import League as LeagueModel
from ..db_models import Season as SeasonModel
from ..schemas.season_schemas import SeasonCreate


def list_season(db: Session):
    query = select(SeasonModel).options(joinedload(SeasonModel.league))

    season = db.execute(query).scalars().all()
    return season


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
