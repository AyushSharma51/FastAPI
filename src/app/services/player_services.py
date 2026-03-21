from fastapi import HTTPException
from sqlalchemy import exists, func, select
from sqlalchemy.orm import Session, joinedload
from ..schemas.player_schemas import PlayerCreate, PlayerMatchStatsUpdate, PlayerUpdate
from ..db_models import Player as PlayerModel, TeamPlayer
from ..db_models import PlayerMatchStat as PlayerMatchStatModel
from ..schemas.player_schemas import PlayerMatchStatsCreate
from ..db_models import League as LeagueModel
from ..db_models import Match
from ..db_models import PlayerMatchStat, Season


# Player Services
#-------------------------------------------------------------------------------------------------------------------
def get_all_players(db: Session):
    query = select(PlayerModel)
    player = db.execute(query).scalars().all()
    return player


def create_a_player(db: Session, player: PlayerCreate):
    """Create a new player"""
    player = PlayerModel(**player.model_dump())
    db.add(player)
    db.commit()
    db.refresh(player)
    return player

def get_player_by_id(db: Session, player_id: int):
    player = db.get(PlayerModel, player_id)

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    return player


# PUT -------------------------------------------------------

def update_player(db: Session, player_id: int, player: PlayerCreate):
    db_player = db.get(PlayerModel, player_id)

    if not db_player:
        raise HTTPException(status_code=404, detail="Player not found")

    db_player.name = player.name
    db_player.birth_date = player.birth_date
    db_player.nationality = player.nationality

    db.commit()
    db.refresh(db_player)

    return db_player

# PATCH ----------------------------------------------------------------

def patch_player(db: Session, player_id: int, player: PlayerUpdate):
    db_player = db.get(PlayerModel, player_id)

    if not db_player:
        raise HTTPException(status_code=404, detail="Player not found")

    update_data = player.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_player, key, value)

    db.commit()
    db.refresh(db_player)

    return db_player

# DELETE --------------------------------------------------------------------

def delete_player(db: Session, player_id: int):
    player = db.get(PlayerModel, player_id)

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    #  Check if player has match stats
    has_stats = db.query(
        exists().where(PlayerMatchStat.player_id == player_id)
    ).scalar()

    #  Check if player in team roster
    has_team = db.query(
        exists().where(TeamPlayer.player_id == player_id)
    ).scalar()

    if has_stats or has_team:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete player with existing records"
        )

    db.delete(player)
    db.commit()

    return {"message": "Player deleted successfully"}


# Player-Match-Stats Services 
#----------------------------------------------------------------------------------------------------------------------

def create_player_stats(db: Session, player_stats: PlayerMatchStatsCreate):
    player_stats = PlayerMatchStatModel(**player_stats.model_dump())
    db.add(player_stats)
    db.commit()
    db.refresh(player_stats)
    return player_stats


def list_player_stats(db: Session):
    query = select(PlayerMatchStatModel).options(
        joinedload(PlayerMatchStatModel.match),
        joinedload(PlayerMatchStatModel.player),
        joinedload(PlayerMatchStatModel.team),  # ✅ add this
    )
    return db.execute(query).scalars().all()

# Player-Stats Services
#------------------------------------------------------------------------------------------------------------------------

def get_player_cumulative_stats(
    db: Session,
    player_id: int,
    year: int | None = None,
    league_name: str | None = None,
    team_id: int | None = None,
    from_date=None,
    to_date=None,
):
    player = db.execute(
        select(PlayerModel).where(PlayerModel.id == player_id)
    ).scalar_one_or_none()

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
        query = query.where(func.strftime("%Y", Season.start_date) == str(year))

    if league_name is not None:
        query = query.where(LeagueModel.name == league_name)

    if from_date is not None:
        query = query.where(Match.date >= from_date)
    if to_date is not None:
        query = query.where(Match.date <= to_date)

    if team_id is not None:
        query = query.where(PlayerMatchStat.team_id == team_id)

    result = db.execute(query).one()

    return {
        "player_id": player.id,
        "player_name": player.name,
        "total_goals": result.total_goals or 0,
        "total_assists": result.total_assists or 0,
        "total_minutes_played": result.total_minutes_played or 0,
        "matches_played": result.matches_played or 0,
    }

def get_player_stat_by_id(db: Session, stat_id: int):
    stat = db.get(PlayerMatchStatModel, stat_id)

    if not stat:
        raise HTTPException(status_code=404, detail="Player match stat not found")

    return stat


def update_player_stat(db: Session, stat_id: int, data: PlayerMatchStatsUpdate):
    stat = db.get(PlayerMatchStatModel, stat_id)

    if not stat:
        raise HTTPException(status_code=404, detail="Player match stat not found")

    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(stat, key, value)

    db.commit()
    db.refresh(stat)

    return stat


def delete_player_stat(db: Session, stat_id: int):
    stat = db.get(PlayerMatchStatModel, stat_id)

    if not stat:
        raise HTTPException(status_code=404, detail="Player match stat not found")

    db.delete(stat)
    db.commit()

    return {"message": "Player stat deleted successfully"}

