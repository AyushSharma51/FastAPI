import pytest
from datetime import date
from pydantic import ValidationError

from src.app.schemas.team_schemas import TeamCreate


# ============================================================
# VALID CASE
# ============================================================

def test_valid_team_creation():
    """
    Scenario: Valid team input
    Expectation: Object should be created successfully
    """
    obj = TeamCreate(
        name="Barcelona",
        city="Barcelona",
        founded_year=1899,
        stadium="Camp Nou",
    )

    assert obj.name == "Barcelona"
    assert obj.founded_year == 1899


# ============================================================
# FOUNDED YEAR VALIDATION
# ============================================================

def test_founded_year_cannot_be_future():
    """
    Scenario: Founded year is in the future
    Expectation: Validation error
    """
    future_year = date.today().year + 1

    with pytest.raises(ValidationError):
        TeamCreate(
            name="Future FC",
            city="Future City",
            founded_year=future_year,
            stadium="Future Stadium",
        )