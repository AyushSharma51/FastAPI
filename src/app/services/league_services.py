from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from ..cache import delete_cache, delete_cache_pattern, get_cache, make_cache_key, set_cache

from ..schemas.league_schemas import LeagueCreate
from ..db_models import League as LeagueModel, Season


# ------------------------------------ GET ALL LEAGUES ------------------------------------

async def get_all_leagues(db: AsyncSession):
    """
    Fetch all leagues that are not soft-deleted.

    Args:
        db (AsyncSession): Database session

    Returns:
        List[LeagueModel]: List of active leagues
    """
    cache_key = make_cache_key("leagues")

    cached = await get_cache(cache_key)
    if cached:
        return cached

    query = select(LeagueModel).where(LeagueModel.is_deleted.is_(False))
    result = await db.execute(query)
    leagues = result.scalars().all()

    leagues_dict = jsonable_encoder(leagues)
    await set_cache(cache_key, leagues_dict, ttl=300)

    return leagues


# ------------------------------------ CREATE A LEAGUE ------------------------------------

async def create_league(db: AsyncSession, league: LeagueCreate):
    """
    Create a new league.

    Args:
        db (AsyncSession): Database session
        league (LeagueCreate): Input schema

    Returns:
        LeagueModel: Created league object

    Raises:
        HTTPException: If league name already exists
    """
    try:
        db_league = LeagueModel(**league.model_dump())
        db.add(db_league)
        await db.commit()
        await db.refresh(db_league)

        await set_cache(make_cache_key("league", id=db_league.id), jsonable_encoder(db_league))
        await delete_cache_pattern("leagues:*")  
        
        return db_league

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Name already exists"
        )


# ------------------------------------ UPDATE A LEAGUE ------------------------------------

async def league_update(db: AsyncSession, league_id: int, league: LeagueCreate):
    """
    Update an existing league.

    Args:
        db (AsyncSession): Database session
        league_id (int): League ID
        league (LeagueCreate): Updated data

    Returns:
        LeagueModel: Updated league

    Raises:
        HTTPException: If league not found or name conflict
    """
    db_league = await db.get(LeagueModel, league_id)

    if db_league is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found"
        )

    update_data = league.model_dump(exclude_unset=True)

    if "name" in update_data:
        db_league.name = update_data["name"]

    try:
        await db.commit()
        await db.refresh(db_league)
        await delete_cache(make_cache_key("league", id=league_id))
        await delete_cache_pattern("leagues:*")

        league_dict = jsonable_encoder(db_league)
        await set_cache(make_cache_key("league", id=league_id), league_dict)

        return db_league

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Name already exists"
        )


# ------------------------------------ DELETE A LEAGUE ------------------------------------

async def delete_league(db: AsyncSession, league_id: int):
    """
    Delete a league:
    - Soft delete if it has related seasons
    - Hard delete if no dependencies

    Args:
        db (AsyncSession): Database session
        league_id (int): League ID

    Returns:
        dict: Deletion message

    Raises:
        HTTPException: If league not found
    """
    league = await db.get(LeagueModel, league_id)

    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found"
        )

    # Check if related seasons exist
    result = await db.execute(
        select(exists().where(Season.league_id == league_id))
    )
    has_seasons = result.scalar()

    if has_seasons:
        # Soft delete
        league.is_deleted = True
        await db.commit()

        await delete_cache(make_cache_key("league", id=league_id))
        await delete_cache_pattern("leagues:*")

        return {"message": "League soft deleted (has seasons)"}

    else:
        # Hard delete
        await db.delete(league)
        await db.commit()

        await delete_cache(make_cache_key("league", id=league_id))
        await delete_cache_pattern("leagues:*")

        return {"message": "League permanently deleted"}