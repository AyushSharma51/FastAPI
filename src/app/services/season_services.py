from ..db_models import Season as SeasonModel
from datetime import date as dt_date
from sqlalchemy import select
from sqlalchemy.orm import Session

def list_season(db:Session):
    query = select(SeasonModel)
    season = db.execute(query).scalars().all()
    return season

def create_season(db:Session,league_id:int,year:int, start_date:dt_date, end_date:dt_date):
    """Create a new season"""
    season = SeasonModel(league_id=league_id, year=year, start_date=start_date, end_date=end_date)
    db.add(season)
    db.commit()
    db.refresh(season)
    return season
