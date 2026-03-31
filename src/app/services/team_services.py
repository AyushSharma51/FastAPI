from datetime import date
from fastapi import HTTPException
from sqlalchemy import case, exists, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..schemas.common_schemas import PaginationParams
from ..db_models import (
    MatchParticipant,
    PlayerMatchStat,
    Team as TeamModel,
    Match,
    Season,
    League,
)
from ..schemas.team_schemas import TeamCreate, TeamPlayersUpdate, TeamUpdate
from ..db_models import TeamPlayer as TeamPlayerModel
from ..schemas.team_schemas import TeamPlayersCreate


# ------------------------------------ TEAM ------------------------------------

async def create_team(db: AsyncSession, team: TeamCreate):
    db_team = TeamModel(**team.model_dump())
    db.add(db_team)
    await db.commit()
    await db.refresh(db_team)
    return db_team


async def get_all_teams(db: AsyncSession, pagination: PaginationParams, name=None):
    query = select(TeamModel)

    if name:
        query = query.where(TeamModel.name.ilike(f"%{name}%"))

    query = query.order_by(TeamModel.id)
    query = query.offset(pagination.offset).limit(pagination.limit)

    result = await db.execute(query)
    return result.scalars().all()


async def get_team_by_id(db: AsyncSession, team_id: int):
    team = await db.get(TeamModel, team_id)

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    return team


async def update_team(db: AsyncSession, team_id: int, team: TeamCreate):
    db_team = await db.get(TeamModel, team_id)

    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")

    db_team.name = team.name
    db_team.city = team.city
    db_team.founded_year = team.founded_year
    db_team.stadium = team.stadium

    await db.commit()
    await db.refresh(db_team)

    return db_team


async def patch_team(db: AsyncSession, team_id: int, team: TeamUpdate):
    db_team = await db.get(TeamModel, team_id)

    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")

    update_data = team.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_team, key, value)

    await db.commit()
    await db.refresh(db_team)

    return db_team


async def delete_team(db: AsyncSession, team_id: int):
    team = await db.get(TeamModel, team_id)

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    result = await db.execute(
        select(exists().where(MatchParticipant.team_id == team_id))
    )
    has_matches = result.scalar()

    if has_matches:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete team with existing matches"
        )

    await db.delete(team)
    await db.commit()

    return {"message": "Team deleted successfully"}


# ------------------------------------ TEAM PLAYERS ------------------------------------

async def create_team_players(db: AsyncSession, team_players: TeamPlayersCreate):

    if not team_players.team_id:
        raise HTTPException(404, "Team not found")

    if not team_players.player_id:
        raise HTTPException(404, "Player not found")

    if not team_players.season_id:
        raise HTTPException(404, "Season not found")

    db_tp = TeamPlayerModel(**team_players.model_dump())

    db.add(db_tp)
    await db.commit()
    await db.refresh(db_tp)

    return db_tp


async def get_all_team_players(db: AsyncSession, pagination: PaginationParams):
    query = select(TeamPlayerModel).options(
        joinedload(TeamPlayerModel.team),
        joinedload(TeamPlayerModel.season),
        joinedload(TeamPlayerModel.player),
    )

    query = query.order_by(TeamPlayerModel.id)
    query = query.offset(pagination.offset).limit(pagination.limit)

    result = await db.execute(query)

    # ✅ FIX: required for joinedload
    return result.scalars().unique().all()


async def get_team_player_by_id(db: AsyncSession, team_player_id: int):
    tp = await db.get(TeamPlayerModel, team_player_id)

    if not tp:
        raise HTTPException(status_code=404, detail="Roster entry not found")

    return tp


async def update_team_player(db: AsyncSession, team_player_id: int, data: TeamPlayersUpdate):
    tp = await db.get(TeamPlayerModel, team_player_id)

    if not tp:
        raise HTTPException(status_code=404, detail="Roster entry not found")

    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(tp, key, value)

    await db.commit()
    await db.refresh(tp)

    return tp


async def delete_team_player(db: AsyncSession, team_player_id: int):
    tp = await db.get(TeamPlayerModel, team_player_id)

    if not tp:
        raise HTTPException(status_code=404, detail="Roster entry not found")

    result = await db.execute(
        select(
            exists().where(
                (PlayerMatchStat.player_id == tp.player_id)
                & (PlayerMatchStat.team_id == tp.team_id)
            )
        )
    )
    has_stats = result.scalar()

    if has_stats:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete roster entry with existing match stats",
        )

    await db.delete(tp)
    await db.commit()

    return {"message": "Roster entry deleted"}


# ------------------------------------ TEAM STATS ------------------------------------

async def get_team_cumulative_stats(
    db: AsyncSession,
    team_id: int,
    year: int | None = None,
    league_name: str | None = None,
    season_id: int | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
):
    result = await db.execute(
        select(TeamModel).where(TeamModel.id == team_id)
    )
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    opponent = MatchParticipant.__table__.alias("opponent")

    query = (
        select(
            func.count(MatchParticipant.id).label("matches_played"),
            func.sum(case((MatchParticipant.score > opponent.c.score, 1), else_=0)).label("wins"),
            func.sum(case((MatchParticipant.score == opponent.c.score, 1), else_=0)).label("draws"),
            func.sum(case((MatchParticipant.score < opponent.c.score, 1), else_=0)).label("losses"),
            func.sum(MatchParticipant.score).label("goals_scored"),
            func.sum(opponent.c.score).label("goals_conceded"),
            func.sum(
                case(
                    (MatchParticipant.score > opponent.c.score, 3),
                    (MatchParticipant.score == opponent.c.score, 1),
                    else_=0,
                )
            ).label("points"),
        )
        .join(Match, Match.id == MatchParticipant.match_id)
        .join(Season, Season.id == Match.season_id)
        .join(League, League.id == Season.league_id)
        .join(
            opponent,
            (MatchParticipant.match_id == opponent.c.match_id)
            & (MatchParticipant.team_id != opponent.c.team_id),
        )
        .where(MatchParticipant.team_id == team_id)
    )

    if year is not None:
        query = query.where(extract("year", Season.start_date) == year)

    if league_name is not None:
        query = query.where(League.name == league_name)

    if season_id is not None:
        query = query.where(Season.id == season_id)

    if from_date is not None:
        query = query.where(Match.date >= from_date)

    if to_date is not None:
        query = query.where(Match.date <= to_date)

    result = await db.execute(query)
    stats = result.one()

    return {
        "team_id": team.id,
        "team_name": team.name,
        "matches_played": stats.matches_played or 0,
        "wins": stats.wins or 0,
        "draws": stats.draws or 0,
        "losses": stats.losses or 0,
        "goals_scored": stats.goals_scored or 0,
        "goals_conceded": stats.goals_conceded or 0,
        "points": stats.points or 0,
    }