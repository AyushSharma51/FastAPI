from datetime import date
from fastapi import HTTPException
from sqlalchemy import case, exists, extract, func, select
from sqlalchemy.orm import Session, joinedload

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

# Team Services
# ---------------------------------------------------------------------------------------------------------------------


def create_team(db: Session, team: TeamCreate):
    """Create a new team"""
    team = TeamModel(**team.model_dump())
    db.add(team)
    db.commit()
    db.refresh(team)
    return team

def get_all_teams(db: Session, pagination: PaginationParams, name=None):
    query = select(TeamModel)

    if name:
        query = query.where(TeamModel.name.ilike(f"%{name}%"))

    query = query.order_by(TeamModel.id)
    query = query.offset(pagination.offset).limit(pagination.limit)

    return db.execute(query).scalars().all()


def get_team_by_id(db: Session, team_id: int):
    team = db.get(TeamModel, team_id)

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    return team


def update_team(db: Session, team_id: int, team: TeamCreate):
    db_team = db.get(TeamModel, team_id)

    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")

    db_team.name = team.name
    db_team.city = team.city
    db_team.founded_year = team.founded_year
    db_team.stadium = team.stadium

    db.commit()
    db.refresh(db_team)

    return db_team


def patch_team(db: Session, team_id: int, team: TeamUpdate):
    db_team = db.get(TeamModel, team_id)

    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")

    update_data = team.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_team, key, value)

    db.commit()
    db.refresh(db_team)

    return db_team


def delete_team(db: Session, team_id: int):
    team = db.get(TeamModel, team_id)

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # 🔍 Check if team used in matches

    has_matches = db.query(MatchParticipant).filter(
        MatchParticipant.team_id == team_id
    ).first()

    if has_matches:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete team with existing matches"
        )

    db.delete(team)
    db.commit()

    return {"message": "Team deleted successfully"}


# Team Player Services
# -----------------------------------------------------------------------------------------------------------------------


def create_team_players(db: Session, team_players: TeamPlayersCreate):

    if not team_players.team_id:
        raise HTTPException(404, "Team not found")

    if not team_players.player_id:
        raise HTTPException(404, "Player not found")

    if not team_players.season_id:
        raise HTTPException(404, "Season not found")

    team_players = TeamPlayerModel(**team_players.model_dump())
    db.add(team_players)
    db.commit()
    db.refresh(team_players)
    return team_players


def get_all_team_players(db: Session, pagination: PaginationParams):
    query = select(TeamPlayerModel).options(
        joinedload(TeamPlayerModel.team),
        joinedload(TeamPlayerModel.season),
        joinedload(TeamPlayerModel.player),
    )

    query = query.order_by(TeamPlayerModel.id)  
    query = query.offset(pagination.offset).limit(pagination.limit)

    return db.execute(query).scalars().all()


def get_team_player_by_id(db: Session, team_player_id: int):
    tp = db.get(TeamPlayerModel, team_player_id)

    if not tp:
        raise HTTPException(status_code=404, detail="Roster entry not found")

    return tp


def update_team_player(db: Session, team_player_id: int, data: TeamPlayersUpdate):
    tp = db.get(TeamPlayerModel, team_player_id)

    if not tp:
        raise HTTPException(status_code=404, detail="Roster entry not found")

    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(tp, key, value)

    db.commit()
    db.refresh(tp)

    return tp


def delete_team_player(db: Session, team_player_id: int):
    tp = db.get(TeamPlayerModel, team_player_id)

    if not tp:
        raise HTTPException(status_code=404, detail="Roster entry not found")

    # 🔍 Check if player has stats in matches
    has_stats = db.query(
        exists().where(
            (PlayerMatchStat.player_id == tp.player_id)
            & (PlayerMatchStat.team_id == tp.team_id)
        )
    ).scalar()

    if has_stats:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete roster entry with existing match stats",
        )
    

    db.delete(tp)
    db.commit()

    return {"message": "Roster entry deleted"}


def get_team_cumulative_stats(
    db: Session,
    team_id: int,
    year: int | None = None,
    league_name: str | None = None,
    season_id: int | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
):
    team = db.execute(
        select(TeamModel).where(TeamModel.id == team_id)
    ).scalar_one_or_none()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # alias for opponent
    opponent = MatchParticipant.__table__.alias("opponent")

    query = (
        select(
            func.count(MatchParticipant.id).label("matches_played"),
            func.sum(
                case(
                    (MatchParticipant.score > opponent.c.score, 1),
                    else_=0,
                )
            ).label("wins"),
            func.sum(
                case(
                    (MatchParticipant.score == opponent.c.score, 1),
                    else_=0,
                )
            ).label("draws"),
            func.sum(
                case(
                    (MatchParticipant.score < opponent.c.score, 1),
                    else_=0,
                )
            ).label("losses"),
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
        # self join to get opponent
        .join(
            opponent,
            (MatchParticipant.match_id == opponent.c.match_id)
            & (MatchParticipant.team_id != opponent.c.team_id),
        )
        .where(MatchParticipant.team_id == team_id)
    )

    # ---------------- FILTERS ---------------- #

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

    # ---------------- EXECUTE ---------------- #

    result = db.execute(query).one()

    return {
        "team_id": team.id,
        "team_name": team.name,
        "matches_played": result.matches_played or 0,
        "wins": result.wins or 0,
        "draws": result.draws or 0,
        "losses": result.losses or 0,
        "goals_scored": result.goals_scored or 0,
        "goals_conceded": result.goals_conceded or 0,
        "points": result.points or 0,
    }
