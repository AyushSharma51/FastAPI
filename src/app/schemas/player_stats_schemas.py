from typing import List

from pydantic import BaseModel

from ..schemas.player_match_stats_schemas import PlayerMatchStats


class PlayerSeasonStats(BaseModel):
    season_id: int
    league: str
    team: str
    match_stats: PlayerMatchStats

    class Config:
        from_attributes = True


class PlayerCumulativeStats(BaseModel):
    player: str
    total_matches: int
    home_matches: int
    away_matches: int
    total_goals: int
    total_assists: int
    total_minutes: int
    seasons: List[PlayerSeasonStats]

    class Config:
        from_attributes = True