from sqlalchemy import select
from sqlalchemy.orm import Session
from ..schemas.player_schemas import PlayerCreate
from ..db_models import Player as PlayerModel


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
