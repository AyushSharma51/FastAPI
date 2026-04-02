from typing import List
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, select, delete, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from ..db_models import Match as MatchModel, MatchParticipant
from ..db_models import MatchParticipant as MatchParticipantModel
from ..db_models import PlayerMatchStat as PlayerMatchStatModel
from ..db_models import Season as SeasonModel
from ..db_models import Team as TeamModel
from ..schemas.match_schemas import MatchCreate
from ..cache import delete_cache_pattern, get_cache, make_cache_key, set_cache, delete_cache

# ------------------------------------ CREATE MATCH ------------------------------------

async def create_a_new_match(db: AsyncSession, matches: List[MatchCreate]):
    results = []

    for match in matches:

        season = await db.get(SeasonModel, match.season_id)

        if not season:
            raise HTTPException(404, "Season not found")

        if len(match.participants) != 2:
            raise HTTPException(400, "Match must have exactly 2 participants")

        team_ids = set()

        for p in match.participants:
            team = await db.get(TeamModel, p.team_id)
            if not team:
                raise HTTPException(404, "Team not found")

            if p.team_id in team_ids:
                raise HTTPException(400, "Duplicate teams not allowed")

            team_ids.add(p.team_id)

        db_match = MatchModel(**match.model_dump(exclude={"participants"}))
        db.add(db_match)
        await db.flush()

        for p in match.participants:
            db_participant = MatchParticipantModel(
                match_id=db_match.id,
                team_id=p.team_id,
                is_home=p.is_home,
            )
            db.add(db_participant)

        await db.commit()

        result = await db.execute(
            select(MatchModel)
            .options(
                joinedload(MatchModel.season).joinedload(SeasonModel.league),
                selectinload(MatchModel.participants).joinedload(MatchParticipantModel.team)
            )
            .where(MatchModel.id == db_match.id)
        )
        db_match = result.unique().scalar_one()  


        # Write-through: cache full match dict, invalidate all list caches
        await set_cache(make_cache_key("match", id=db_match.id), jsonable_encoder(db_match))
        await delete_cache_pattern("matches:*")  # new match affects all paginated lists

        results.append(db_match)

    return results


# ------------------------------------ GET ALL MATCHES ------------------------------------

async def get_all_matches(db, filters, date_range, sort_params, pagination):

    #  CREATE UNIQUE CACHE KEY
    cache_key = make_cache_key(
        "matches",
        status=filters.status.value if filters.status else None,
        from_date=str(date_range.from_date),
        to_date=str(date_range.to_date),
        sort_by=sort_params.sort_by,
        sort_order=sort_params.sort_order,
        offset=pagination.offset,
        limit=pagination.limit
    )

    # CHECK CACHE
    cached = await get_cache(cache_key)
    if cached:
        print("CACHE HIT")
        return cached
    
    query = select(MatchModel).options(
        joinedload(MatchModel.season).joinedload(SeasonModel.league),
        selectinload(MatchModel.participants).joinedload(MatchParticipantModel.team)
    )

    if filters.status:
        query = query.where(MatchModel.status == filters.status.value)

    if date_range.from_date:
        query = query.where(MatchModel.date >= date_range.from_date)
    if date_range.to_date:
        query = query.where(MatchModel.date <= date_range.to_date)

    total_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = total_result.scalar()

    if sort_params.sort_by:
        sort_col = getattr(MatchModel, sort_params.sort_by)
        if sort_params.sort_order == "desc":
            sort_col = sort_col.desc()
        query = query.order_by(sort_col)
    else:
        query = query.order_by(MatchModel.id)

    query = query.offset(pagination.offset).limit(pagination.limit)

    result = await db.execute(query)
    matches = result.scalars().unique().all()

    response = {
        "total": total,
        "page": pagination.offset // pagination.limit if pagination.limit else 0,
        "limit": pagination.limit,
        "matches": matches 
    }

    json_data = jsonable_encoder(response)
    
    #  STORE IN CACHE
    await set_cache(cache_key, json_data, ttl=180)

    return response


# ------------------------------------ GET MATCH BY ID ------------------------------------

async def get_match_by_id(db, match_id):
    # Single match
    cache_key = make_cache_key("match", id=match_id)

    #  Check cache
    cached = await get_cache(cache_key)
    if cached:
        return cached
    
    result = await db.execute(
        select(MatchModel)
        .options(
            joinedload(MatchModel.season).joinedload(SeasonModel.league),
            selectinload(MatchModel.participants).joinedload(MatchParticipantModel.team)
        )
        .where(MatchModel.id == match_id)
    )

    match = result.unique().scalar_one_or_none()  

    if match is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    json_data = jsonable_encoder(match)

    await set_cache(cache_key, json_data)

    return match


# ------------------------------------ UPDATE MATCH ------------------------------------

async def update_a_match(db, match_id, update):
    db_match = await db.get(MatchModel, match_id)

    if db_match is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )

    update_data = update.model_dump(exclude_unset=True)

    if "venue" in update_data:
        db_match.venue = update_data["venue"]

    if "date" in update_data:
        db_match.date = update_data["date"]

    if "status" in update_data:
        db_match.status = update_data["status"]

    await db.commit()

    result = await db.execute(
        select(MatchModel)
        .options(
            joinedload(MatchModel.season).joinedload(SeasonModel.league),
            selectinload(MatchModel.participants).joinedload(MatchParticipantModel.team)
        )
        .where(MatchModel.id == db_match.id)
    )

    db_match = result.unique().scalar_one()  


    # Invalidate both the single match and all list caches
    await delete_cache(make_cache_key("match", id=match_id))
    await delete_cache_pattern("matches:*")

    match_dict = jsonable_encoder(db_match)
    await set_cache(make_cache_key("match", id=match_id), match_dict)

    return db_match


# ------------------------------------ REPLACE MATCH ------------------------------------

async def replace_a_match(db, match_id, match):
    db_match = await db.get(MatchModel, match_id)

    if db_match is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )

    db_match.venue = match.venue
    db_match.date = match.date
    db_match.status = match.status.value

    await db.commit()

    result = await db.execute(
        select(MatchModel)
        .options(
            joinedload(MatchModel.season).joinedload(SeasonModel.league),
            selectinload(MatchModel.participants).joinedload(MatchParticipantModel.team)
        )
        .where(MatchModel.id == db_match.id)
    )

    db_match = result.unique().scalar_one()  
    
    await delete_cache(make_cache_key("match", id=match_id))
    await delete_cache_pattern("matches:*")

    match_dict = jsonable_encoder(db_match)
    await set_cache(make_cache_key("match", id=match_id), match_dict)

    return db_match


# ------------------------------------ DELETE MATCH ------------------------------------

async def delete_a_match(db, match_id):
    match = await db.get(MatchModel, match_id)

    if not match:
        raise HTTPException(404, "Match not found")

    result = await db.execute(
        select(exists().where(PlayerMatchStatModel.match_id == match_id))
    )
    has_stats = result.scalar()

    if has_stats:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete match because it has related player stats"
        )

    await db.execute(
        delete(MatchParticipant).where(
            MatchParticipant.match_id == match_id
        )
    )

    await db.delete(match)
    await db.commit()

    await delete_cache(make_cache_key("match", id=match_id))
    await delete_cache_pattern("matches:*")
    
    return {"message": "Match deleted successfully"}