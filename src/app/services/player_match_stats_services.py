from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..schemas.player_match_stats_schemas import PlayerMatchStatsCreate
from ..db_models import PlayerMatchStat as PlayerMatchStatModel


def create_player_stats(db: Session, player_stats: PlayerMatchStatsCreate):
    player_stats = PlayerMatchStatModel(**player_stats.model_dump())
    db.add(player_stats)
    db.commit()
    db.refresh(player_stats)
    return player_stats


def list_player_stats(db: Session):
    query = select(PlayerMatchStatModel).options(
        joinedload(PlayerMatchStatModel.match), joinedload(PlayerMatchStatModel.player)
    )

    player_stats = db.execute(query).scalars().all()
    return player_stats
