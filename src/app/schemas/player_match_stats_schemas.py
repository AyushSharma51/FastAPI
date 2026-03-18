from pydantic import BaseModel, Field, model_validator
from ..schemas.match_schemas import MatchDetails
from ..schemas.player_schemas import  PlayerLite
# from ..schemas.match_schemas import MatchResponse


class PlayerMatchStats(BaseModel):
    match_id: int = Field(gt=0)
    player_id: int = Field(gt=0)
    goals: int = Field(ge=0)
    assists: int = Field(ge=0)
    minutes_played: int = Field(ge=0, le=120)

    @model_validator(mode="after")
    def validate_minutes(self):
        if self.minutes_played == 0 and (self.goals > 0 or self.assists > 0):
            raise ValueError("Player with 0 minutes cannot have goals or assists")
        return self

    class Config:
        from_attributes = True


class PlayerMatchStatsCreate(PlayerMatchStats):
    pass


class PlayerMatchStatsResponse(PlayerMatchStats):
    id: int
    player: PlayerLite
    match: MatchDetails

    class Config:
        from_attributes = True
