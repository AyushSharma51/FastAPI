from sqlalchemy import select
from sqlalchemy.orm import Session
from..db_models import Standing as StandingsModel


def create_standing(db:Session,season_id:int, team_id:int,matches_played:int, wins:int, draws:int, losses:int, points:int):
    
    standings = StandingsModel(season_id=season_id, team_id=team_id,matches_played=matches_played, wins=wins, draws=draws, losses=losses, points=points)
    db.add(standings)
    db.commit()
    db.refresh(standings)
    return standings

def list_standings(db:Session):
    query = select(StandingsModel)
    stadings = db.execute(query).scalars().all()
    return stadings

