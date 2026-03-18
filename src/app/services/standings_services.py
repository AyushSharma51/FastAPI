from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from ..db_models import Standing as StandingsModel
from ..schemas.standings_schemas import StandingsCreate


def create_standing(
    db: Session, standing:StandingsCreate

):
    standings = StandingsModel(**standing.model_dump())
    db.add(standings)
    db.commit()
    db.refresh(standings)
    return standings


def list_standings(db: Session):
    query=select(StandingsModel).options(
        joinedload(StandingsModel.season),
        joinedload(StandingsModel.team)
    )

    standings = db.execute(query).scalars().all()
    return standings


#update standings for other fields