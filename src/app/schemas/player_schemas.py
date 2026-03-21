from datetime import date 
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator



# Player Schema

class PlayerLite(BaseModel):
    name: str = Field(min_length=3, max_length=99)


class Player(PlayerLite):

    birth_date: date
    nationality: str
  

    @field_validator("name", "nationality")
    @classmethod
    def normalize_name(cls, value):
        if value is not None:
            return value.strip().lower()
        return value


class PlayerCreate(Player):
    pass


class PlayerResponse(Player):
    id: int

    class Config:
        from_attributes = True

class PlayerUpdate(BaseModel):
    name: Optional[str] = None
    birth_date: Optional[date] = None
    nationality: Optional[str] = None


# Player-Stats Schema


class PlayerCumulativeStatsQuery(BaseModel):
    year: Optional[int] = None
    league_name: Optional[str] = None  # e.g. "Champions League"
    team_id: Optional[int] = None  # filter stats to when player was at this team
    from_date: Optional[date] = None  # match date >= from_date
    to_date: Optional[date] = None  # match date <= to_date


class PlayerCumulativeStatsResponse(BaseModel):
    player_id: int
    player_name: str
    total_goals: int
    total_assists: int
    total_minutes_played: int
    matches_played: int

# Player-Match-Stats Schema

class PlayerMatchStats(BaseModel):
    match_id: int = Field(gt=0)
    player_id: int = Field(gt=0)
    team_id: int = Field(gt=0)  # ✅ add this
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
 
    class Config:
        from_attributes = True


class PlayerMatchStatsUpdate(BaseModel):
    goals: Optional[int] = Field(default=None, ge=0)
    assists: Optional[int] = Field(default=None, ge=0)
    minutes_played: Optional[int] = Field(default=None, ge=0, le=120)
