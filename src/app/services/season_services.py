from fastapi import HTTPException
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..db_models import League as LeagueModel, Season, Match
from ..db_models import Season as SeasonModel
from ..schemas.season_schemas import SeasonCreate, SeasonUpdate


# -------------------------------------- LIST --------------------------------------


async def list_season(db: AsyncSession):
    query = select(SeasonModel).options(joinedload(SeasonModel.league))

    result = await db.execute(query)

    # ✅ FIX
    seasons = result.scalars().unique().all()

    return seasons


# ----------------------------------- CREATE --------------------------------------


async def create_season(db: AsyncSession, season: SeasonCreate):

    # Check league exists
    result = await db.execute(
        select(LeagueModel).where(LeagueModel.id == season.league_id)
    )
    league = result.scalar_one_or_none()

    if not league:
        raise HTTPException(status_code=404, detail="League not found")

    db_season = SeasonModel(**season.model_dump())

    db.add(db_season)
    await db.commit()

    result = await db.execute(
        select(SeasonModel)
        .options(joinedload(SeasonModel.league))
        .where(SeasonModel.id == db_season.id)
    )

    # ✅ FIX
    db_season = result.unique().scalar_one()

    return db_season


# -------------------------------------- REPLACE --------------------------------------


async def update_season(db: AsyncSession, season_id: int, season: SeasonCreate):
    db_season = await db.get(Season, season_id)

    if not db_season:
        raise HTTPException(status_code=404, detail="Season not found")

    db_season.league_id = season.league_id
    db_season.country = season.country
    db_season.start_date = season.start_date
    db_season.end_date = season.end_date

    await db.commit()

    result = await db.execute(
        select(SeasonModel)
        .options(joinedload(SeasonModel.league))
        .where(SeasonModel.id == db_season.id)
    )

    # ✅ FIX
    db_season = result.unique().scalar_one()

    return db_season


# -------------------------------------- PATCH --------------------------------------


async def patch_season(
    db: AsyncSession, season_id: int, season: SeasonUpdate
) -> SeasonModel:

    db_season = await db.get(Season, season_id)

    if not db_season:
        raise HTTPException(status_code=404, detail="Season not found")

    # 🔹 Update only provided fields
    update_data = season.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_season, key, value)

    await db.commit()

    # 🔥 IMPORTANT: reload with league (avoid MissingGreenlet)
    result = await db.execute(
        select(SeasonModel)
        .options(joinedload(SeasonModel.league))
        .where(SeasonModel.id == db_season.id)
    )

    # ✅ FIX
    db_season = result.unique().scalar_one()

    return db_season


# -------------------------------------- DELETE --------------------------------------


async def delete_season(db: AsyncSession, season_id: int):
    season = await db.get(Season, season_id)

    if not season:
        raise HTTPException(status_code=404, detail="Season not found")

    # 🔹 Check if matches exist (async-safe)
    result = await db.execute(select(exists().where(Match.season_id == season_id)))
    has_matches = result.scalar()

    if has_matches:
        raise HTTPException(
            status_code=400, detail="Cannot delete season with existing matches"
        )

    await db.delete(season)
    await db.commit()

    return {"message": "Season deleted successfully"}