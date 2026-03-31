from fastapi import HTTPException
from sqlalchemy import exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

from ..schemas.common_schemas import PaginationParams
from ..schemas.player_schemas import PlayerCreate, PlayerMatchStatsUpdate, PlayerUpdate
from ..db_models import Player as PlayerModel, Team, TeamPlayer
from ..db_models import PlayerMatchStat as PlayerMatchStatModel
from ..db_models import League as LeagueModel
from ..db_models import Match, PlayerMatchStat, Season


# ------------------------------------ PLAYERS ------------------------------------

async def get_all_players(db: AsyncSession, pagination: PaginationParams, name=None):
    query = select(PlayerModel)

    if name:
        query = query.where(PlayerModel.name.ilike(f"%{name}%"))

    query = query.order_by(PlayerModel.id)
    query = query.offset(pagination.offset).limit(pagination.limit)

    result = await db.execute(query)
    return result.scalars().all()


async def create_a_player(db: AsyncSession, player: PlayerCreate):
    db_player = PlayerModel(**player.model_dump())
    db.add(db_player)
    await db.commit()
    await db.refresh(db_player)
    return db_player


async def get_player_by_id(db: AsyncSession, player_id: int):
    player = await db.get(PlayerModel, player_id)

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    return player


# ------------------------------------ UPDATE ------------------------------------

async def update_player(db: AsyncSession, player_id: int, player: PlayerCreate):
    db_player = await db.get(PlayerModel, player_id)

    if not db_player:
        raise HTTPException(status_code=404, detail="Player not found")

    db_player.name = player.name
    db_player.birth_date = player.birth_date
    db_player.nationality = player.nationality

    await db.commit()
    await db.refresh(db_player)

    return db_player


async def patch_player(db: AsyncSession, player_id: int, player: PlayerUpdate):
    db_player = await db.get(PlayerModel, player_id)

    if not db_player:
        raise HTTPException(status_code=404, detail="Player not found")

    update_data = player.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_player, key, value)

    await db.commit()
    await db.refresh(db_player)

    return db_player


# ------------------------------------ DELETE ------------------------------------

async def delete_player(db: AsyncSession, player_id: int):
    player = await db.get(PlayerModel, player_id)

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    # check stats
    result = await db.execute(
        select(exists().where(PlayerMatchStat.player_id == player_id))
    )
    has_stats = result.scalar()

    # check team
    result = await db.execute(
        select(exists().where(TeamPlayer.player_id == player_id))
    )
    has_team = result.scalar()

    if has_stats or has_team:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete player with existing records"
        )

    await db.delete(player)
    await db.commit()

    return {"message": "Player deleted successfully"}


# ------------------------------------ PLAYER STATS ------------------------------------

async def create_player_stats(db: AsyncSession, data):
    player = await db.get(PlayerModel, data.player_id)
    if not player:
        raise HTTPException(404, "Player not found")

    match = await db.get(Match, data.match_id)
    if not match:
        raise HTTPException(404, "Match not found")

    team = await db.get(Team, data.team_id)
    if not team:
        raise HTTPException(404, "Team not found")

    stats = PlayerMatchStatModel(**data.model_dump())

    try:
        db.add(stats)
        await db.commit()
        await db.refresh(stats)
        return stats

    except IntegrityError:
        await db.rollback()
        raise HTTPException(400, "Invalid stats data")


async def list_player_stats(db: AsyncSession, pagination: PaginationParams):
    query = select(PlayerMatchStatModel).options(
        joinedload(PlayerMatchStatModel.match),
        joinedload(PlayerMatchStatModel.player),
        joinedload(PlayerMatchStatModel.team),
    )

    query = query.order_by(PlayerMatchStatModel.id)
    query = query.offset(pagination.offset).limit(pagination.limit)

    result = await db.execute(query)

    # ✅ FIX: required when using joinedload
    return result.scalars().unique().all()


# ------------------------------------ CUMULATIVE STATS ------------------------------------

async def get_player_cumulative_stats(
    db: AsyncSession,
    player_id: int,
    year: int | None = None,
    league_name: str | None = None,
    team_id: int | None = None,
    from_date=None,
    to_date=None,
):
    player_result = await db.execute(
        select(PlayerModel).where(PlayerModel.id == player_id)
    )
    player = player_result.scalar_one_or_none()

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    query = (
        select(
            func.sum(PlayerMatchStat.goals).label("total_goals"),
            func.sum(PlayerMatchStat.assists).label("total_assists"),
            func.sum(PlayerMatchStat.minutes_played).label("total_minutes_played"),
            func.count(PlayerMatchStat.id).label("matches_played"),
        )
        .join(Match, Match.id == PlayerMatchStat.match_id)
        .join(Season, Season.id == Match.season_id)
        .join(LeagueModel, LeagueModel.id == Season.league_id)
        .where(PlayerMatchStat.player_id == player_id)
    )

    if year is not None:
        query = query.where(func.extract("year", Season.start_date) == year)

    if league_name is not None:
        query = query.where(LeagueModel.name == league_name)

    if from_date is not None:
        query = query.where(Match.date >= from_date)
    if to_date is not None:
        query = query.where(Match.date <= to_date)

    if team_id is not None:
        query = query.where(PlayerMatchStat.team_id == team_id)

    result = await db.execute(query)
    stats = result.one()

    return {
        "player_id": player.id,
        "player_name": player.name,
        "total_goals": stats.total_goals or 0,
        "total_assists": stats.total_assists or 0,
        "total_minutes_played": stats.total_minutes_played or 0,
        "matches_played": stats.matches_played or 0,
    }


# ------------------------------------ SINGLE STAT ------------------------------------

async def get_player_stat_by_id(db: AsyncSession, stat_id: int):
    result = await db.execute(
        select(PlayerMatchStatModel)
        .options(
            joinedload(PlayerMatchStatModel.player),
            joinedload(PlayerMatchStatModel.match),
            joinedload(PlayerMatchStatModel.team),
        )
        .where(PlayerMatchStatModel.id == stat_id)
    )

    stat = result.unique().scalar_one_or_none()

    if not stat:
        raise HTTPException(status_code=404, detail="Player match stat not found")

    return stat


async def update_player_stat(db: AsyncSession, stat_id: int, data: PlayerMatchStatsUpdate):
    result = await db.execute(
        select(PlayerMatchStatModel)
        .options(
            joinedload(PlayerMatchStatModel.player),
            joinedload(PlayerMatchStatModel.match),
            joinedload(PlayerMatchStatModel.team),
        )
        .where(PlayerMatchStatModel.id == stat_id)
    )

    stat = result.unique().scalar_one_or_none()

    if not stat:
        raise HTTPException(status_code=404, detail="Player match stat not found")

    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(stat, key, value)

    await db.commit()
    await db.refresh(stat)

    return stat


async def delete_player_stat(db: AsyncSession, stat_id: int):
    stat = await db.get(PlayerMatchStatModel, stat_id)

    if not stat:
        raise HTTPException(status_code=404, detail="Player match stat not found")

    await db.delete(stat)
    await db.commit()

    return {"message": "Player stat deleted successfully"}