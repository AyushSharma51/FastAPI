from typing import Optional
from pydantic import BaseModel, Field, field_validator
from datetime import date 

from ..schemas.player_schemas import PlayerResponse
from ..schemas.season_schemas import SeasonResponsewoLeague


class TeamBase(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    city: str = Field(min_length=2, max_length=50)
    founded_year: int = Field(ge=1800, le=2030)
    stadium: Optional[str] = Field(None, min_length=3, max_length=100)

    @field_validator("founded_year")
    def validate_year(cls, value):
        if value > date.today().year:
            raise ValueError("Founded year cannot be in the future")
        return value

class TeamCreate(TeamBase):
    pass

class TeamResponse(TeamBase):
    id: int

    class Config:
        from_attributes = True

class TeamNameResponse(BaseModel):
    name: str 
    class Config:
        from_attributes = True



# Team Players Schema 
class TeamPlayers(BaseModel):
    team_id: int = Field(gt=0)
    player_id: int = Field(gt=0)
    season_id: int = Field(gt=0)
    jersey_number: int = Field(ge=1, le=99)


class TeamPlayersUpdate(BaseModel):
    jersey_number: Optional[int] = Field(default=None, ge=1, le=99)


class TeamPlayersCreate(TeamPlayers):
    pass


class TeamPlayersResponse(TeamPlayers):
    id: int
    team:TeamResponse
    player:PlayerResponse
    season:SeasonResponsewoLeague
    class Config:
        from_attributes = True
        

class TeamPlayersLite(BaseModel):
    team: TeamNameResponse
    class Config:
        from_attributes = True

class TeamCumulativeStatsQuery(BaseModel):
    year: Optional[int] = None
    league_name: Optional[str] = None  # e.g. "Champions League"
    season_id: Optional[int] = None 
    from_date: Optional[date] = None  # match date >= from_date
    to_date: Optional[date] = None  # match date <= to_date

class TeamUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    founded_year: Optional[int] = None
    stadium: Optional[str] = None


class TeamCumulativeStatsResponse(BaseModel):
    team_id: int
    team_name: str
    matches_played: int
    wins: int
    draws: int
    losses: int
    goals_scored: int
    goals_conceded: int
    points: int