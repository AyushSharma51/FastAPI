import pytest
from datetime import date
from pydantic import ValidationError

from src.app.schemas.player_schemas import (
    PlayerCreate,
    PlayerMatchStatsCreate,
)


# ============================================================
# PLAYER NORMALIZATION
# ============================================================

def test_name_and_nationality_normalization():
    """
    Scenario: Input has spaces and uppercase
    Expectation: Values should be trimmed and converted to lowercase
    """
    obj = PlayerCreate(
        name="  Lionel Messi  ",
        birth_date=date(1987, 6, 24),
        nationality="  Argentina  ",
    )

    assert obj.name == "lionel messi"
    assert obj.nationality == "argentina"


# ============================================================
# PLAYER MATCH STATS VALIDATION
# ============================================================

def test_valid_player_match_stats():
    """
    Scenario: Valid stats
    Expectation: Object created successfully
    """
    obj = PlayerMatchStatsCreate(
        match_id=1,
        player_id=1,
        team_id=1,
        goals=1,
        assists=1,
        minutes_played=90,
    )

    assert obj.goals == 1


def test_zero_minutes_with_stats_should_fail():
    """
    Scenario: Player has 0 minutes but goals/assists > 0
    Expectation: Validation error
    """
    with pytest.raises(ValidationError):
        PlayerMatchStatsCreate(
            match_id=1,
            player_id=1,
            team_id=1,
            goals=1,
            assists=0,
            minutes_played=0,
        )


def test_zero_minutes_with_no_stats_allowed():
    """
    Scenario: Player has 0 minutes and no goals/assists
    Expectation: Allowed
    """
    obj = PlayerMatchStatsCreate(
        match_id=1,
        player_id=1,
        team_id=1,
        goals=0,
        assists=0,
        minutes_played=0,
    )

    assert obj.minutes_played == 0