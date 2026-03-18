from enum import Enum
from pydantic import BaseModel


class LeagueName(str, Enum):
    champions_league = "champions league"
    premier_league = "premier league"
    la_liga = "la liga"
    bundesliga = "bundesliga"
    serie_a = "serie a"
    ligue_1 = "ligue 1"


class League(BaseModel):
    name: LeagueName


class LeagueCreate(League):
    pass


class LeagueResponse(League):
    id: int

    class Config:
        from_attributes = True
