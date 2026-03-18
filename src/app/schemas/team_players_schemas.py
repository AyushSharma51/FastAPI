from pydantic import BaseModel, Field

from ..schemas.player_schemas import PlayerResponse
from ..schemas.season_schemas import SeasonResponsewoLeague

from ..schemas.team_schemas import TeamNameResponse, TeamResponse


class TeamPlayers(BaseModel):
    team_id: int = Field(gt=0)
    player_id: int = Field(gt=0)
    season_id: int = Field(gt=0)
    jersey_number: int = Field(ge=1, le=99)



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
