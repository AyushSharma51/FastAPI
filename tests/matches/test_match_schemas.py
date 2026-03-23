import pytest
from datetime import date, timedelta
from pydantic import ValidationError

from src.app.schemas.match_schemas import MatchCreate, Status


# ============================================================
# VALID CASE
# ============================================================

def test_valid_match_creation():
    """
    Scenario: Valid match input
    Expectation: Object should be created successfully
    """
    obj = MatchCreate(
        season_id=1,
        venue="  Emirates Stadium  ",
        date=date.today() + timedelta(days=1),
        status=Status.upcoming,
        participants=[
            {"team_id": 1, "is_home": True},
            {"team_id": 2, "is_home": False},
        ],
    )

    # Venue should be normalized
    assert obj.venue == "emirates stadium"


# ============================================================
# DATE VALIDATION
# ============================================================

def test_upcoming_match_cannot_be_past():
    """
    Scenario: Upcoming match with past date
    Expectation: Validation error
    """
    with pytest.raises(ValidationError):
        MatchCreate(
            season_id=1,
            venue="Stadium",
            date=date.today() - timedelta(days=1),  # past
            status=Status.upcoming,
            participants=[
                {"team_id": 1, "is_home": True},
                {"team_id": 2, "is_home": False},
            ],
        )


# ============================================================
# PARTICIPANTS VALIDATION
# ============================================================

def test_must_have_two_participants():
    """
    Scenario: Only one participant provided
    Expectation: Validation error
    """
    with pytest.raises(ValidationError):
        MatchCreate(
            season_id=1,
            venue="Stadium",
            date=date.today(),
            status=Status.completed,
            participants=[
                {"team_id": 1, "is_home": True},
            ],
        )


def test_must_have_one_home_one_away():
    """
    Scenario: Both teams marked as home
    Expectation: Validation error
    """
    with pytest.raises(ValidationError):
        MatchCreate(
            season_id=1,
            venue="Stadium",
            date=date.today(),
            status=Status.completed,
            participants=[
                {"team_id": 1, "is_home": True},
                {"team_id": 2, "is_home": True},
            ],
        )


def test_teams_must_be_different():
    """
    Scenario: Same team used twice
    Expectation: Validation error
    """
    with pytest.raises(ValidationError):
        MatchCreate(
            season_id=1,
            venue="Stadium",
            date=date.today(),
            status=Status.completed,
            participants=[
                {"team_id": 1, "is_home": True},
                {"team_id": 1, "is_home": False},
            ],
        )


# ============================================================
# OPTIONAL EDGE CASES
# ============================================================

def test_completed_match_can_have_past_date():
    """
    Scenario: Completed match in past
    Expectation: Allowed
    """
    obj = MatchCreate(
        season_id=1,
        venue="Stadium",
        date=date.today() - timedelta(days=1),
        status=Status.completed,
        participants=[
            {"team_id": 1, "is_home": True},
            {"team_id": 2, "is_home": False},
        ],
    )

    assert obj.status == Status.completed