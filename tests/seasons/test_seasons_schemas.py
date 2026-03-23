"""
Unit tests for season_schemas.py
──────────────────────────────────
Type: Unit — no DB, no HTTP, pure Pydantic validation.
Only tests custom logic (@model_validator on Season).
Plain field declarations (SeasonUpdate, SeasonResponse) are skipped
— those test Pydantic itself, not our code.
"""

from datetime import date
import pytest
from pydantic import ValidationError

from src.app.schemas.season_schemas import SeasonCreate


class TestSeasonDateValidator:

    def test_valid_dates_accepted(self):
        obj = SeasonCreate(
            league_id=1,
            country="England",
            start_date=date(2025, 8, 1),
            end_date=date(2026, 5, 31),
        )
        assert obj.start_date < obj.end_date

    def test_same_start_and_end_date_rejected(self):
        with pytest.raises(ValidationError) as exc_info:
            SeasonCreate(
                league_id=1,
                country="England",
                start_date=date(2025, 8, 1),
                end_date=date(2025, 8, 1),
            )
        assert "same date" in str(exc_info.value).lower()

    def test_end_before_start_accepted(self):
        """
        Current validator only blocks equal dates, not reversed ranges.
        This test documents that behaviour — update it if the validator
        is tightened to also reject end_date < start_date.
        """
        obj = SeasonCreate(
            league_id=1,
            country="England",
            start_date=date(2026, 5, 31),
            end_date=date(2025, 8, 1),
        )
        assert obj.end_date < obj.start_date  # allowed by current logic
