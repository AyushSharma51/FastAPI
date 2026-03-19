from pydantic import BaseModel, Field, computed_field


class TeamStandingEntry(BaseModel):
    """A single team's standing row within a season."""

    team_id: int
    team_name: str
    season_id: int
    league_id: int
    league_name: str

    played: int = Field(
        description="Total matches played (score is not None for both sides)"
    )
    wins: int
    draws: int
    losses: int
    goals_for: int = Field(description="Total goals scored by this team")
    goals_against: int = Field(description="Total goals conceded by this team")

    @computed_field  # type: ignore[misc]
    @property
    def goal_difference(self) -> int:
        return self.goals_for - self.goals_against

    @computed_field  # type: ignore[misc]
    @property
    def points(self) -> int:
        """Standard football points: win=3, draw=1, loss=0."""
        return self.wins * 3 + self.draws

    model_config = {"from_attributes": True}


class StandingsResponse(BaseModel):
    """Paginated standings response."""

    season_id: int
    league_id: int
    league_name: str
    total_teams: int
    standings: list[TeamStandingEntry]
