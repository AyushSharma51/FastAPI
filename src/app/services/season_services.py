from ..db_models import Season as SeasonModel, League as LeagueModel
from ..schemas.season_schemas import SeasonCreate
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from ..schemas.season_schemas import LEAGUE_COUNTRY_MAP
from fastapi import HTTPException


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

    #  Validate league-country rule
    expected_country = LEAGUE_COUNTRY_MAP.get(league.name)

    if expected_country and season.country != expected_country.value:
        raise HTTPException(
            status_code=400,
            detail=f"{league.name} can only be played in {expected_country.value}",
        )

    #  Create season
    season = SeasonModel(**season.model_dump())

    db.add(season)
    db.commit()
    db.refresh(season)

    return season
