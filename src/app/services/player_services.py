from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import date as dt_date
from ..db_models import Player as PlayerModel



def get_all_players(db: Session):
    query = select(PlayerModel)
    player = db.execute(query).scalars().all()
    return player

def create_a_player(db:Session, name:str, birth_date:dt_date, nationality:str):
    """Create a new player"""
    player = PlayerModel(name=name, birth_date=birth_date, nationality=nationality)
    db.add(player)
    db.commit()
    db.refresh(player)
    return player
