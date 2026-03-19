from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload
from ..schemas.player_schemas import PlayerCreate
from ..db_models import Player as PlayerModel
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

