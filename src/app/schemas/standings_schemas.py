from pydantic import BaseModel, Field, model_validator



class Standings(BaseModel):
    season_id: int = Field(ge=0)
    team_id: int = Field(ge=0)
    matches_played: int = Field(ge=0)
    wins: int = Field(ge=0)
    draws: int = Field(ge=0)
    losses: int = Field(ge=0)
    points: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_standings(self):

        # Check matches consistency
        if self.matches_played != (self.wins + self.draws + self.losses):
            raise ValueError(
                "matches_played must equal wins + draws + losses"
            )

        # Validate points
        expected_points = self.wins * 3 + self.draws

        if self.points != expected_points:
            raise ValueError(
                f"points should be {expected_points} based on wins and draws"
            )

        return self


class StandingsCreate(Standings):
    pass


class StandingsResponse(Standings):
    id: int

    class Config:
        from_attributes = True
