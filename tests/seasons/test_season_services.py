import pytest
from datetime import date
from fastapi import HTTPException

from src.app.db_models import Season, Match, League as LeagueModel
from src.app.schemas.season_schemas import SeasonCreate, SeasonUpdate
from src.app.services.season_services import (
    list_season,
    create_season,
    update_season,
    patch_season,
    delete_season,
)

# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture()
def league(db_session):
    """
    Creates a League in DB for tests that require a valid foreign key.
    """
    league = LeagueModel(name="Test League")
    db_session.add(league)
    db_session.commit()
    db_session.refresh(league)
    return league


@pytest.fixture()
def season(db_session, league):
    """
    Creates a Season linked to the above league.
    Used for update, patch, delete tests.
    """
    season = Season(
        league_id=league.id,
        country="England",
        start_date=date(2025, 8, 1),
        end_date=date(2026, 5, 31),
    )
    db_session.add(season)
    db_session.commit()
    db_session.refresh(season)
    return season


# ============================================================
# LIST SEASON
# ============================================================

class TestListSeason:

    def test_returns_empty_list(self, db_session):
        """
        If no seasons exist in DB → should return empty list.
        """
        assert list_season(db_session) == []

    def test_returns_seasons(self, db_session, season):
        """
        After inserting a season → list should return it.
        Also checks joinedload (league relationship is loaded).
        """
        result = list_season(db_session)

        assert len(result) == 1
        assert result[0].id == season.id

        # joinedload ensures league is already loaded (no lazy query)
        assert result[0].league is not None


# ============================================================
# CREATE SEASON
# ============================================================

class TestCreateSeason:

    def test_creates_season(self, db_session, league):
        """
        Valid input → season should be created and persisted.
        """
        result = create_season(
            db_session,
            SeasonCreate(
                league_id=league.id,
                country="Spain",
                start_date=date(2025, 8, 1),
                end_date=date(2026, 5, 31),
            ),
        )

        # DB generated ID should exist
        assert result.id is not None
        assert result.country == "Spain"

    def test_invalid_league_raises_404(self, db_session):
        """
        If league_id does not exist → should raise 404.
        """
        with pytest.raises(HTTPException) as exc:
            create_season(
                db_session,
                SeasonCreate(
                    league_id=999,  # invalid FK
                    country="Spain",
                    start_date=date(2025, 8, 1),
                    end_date=date(2026, 5, 31),
                ),
            )

        assert exc.value.status_code == 404


# ============================================================
# UPDATE SEASON (PUT)
# ============================================================

class TestUpdateSeason:

    def test_updates_all_fields(self, db_session, season, league):
        """
        PUT behavior → replaces all fields of the season.
        """
        result = update_season(
            db_session,
            season.id,
            SeasonCreate(
                league_id=league.id,
                country="Germany",
                start_date=date(2026, 1, 1),
                end_date=date(2026, 12, 1),
            ),
        )

        # Verify full replacement
        assert result.country == "Germany"
        assert result.start_date == date(2026, 1, 1)

    def test_missing_season_raises_404(self, db_session):
        """
        Updating a non-existent season → should raise 404.
        """
        with pytest.raises(HTTPException) as exc:
            update_season(
                db_session,
                999,  # invalid ID
                SeasonCreate(
                    league_id=1,
                    country="X",
                    start_date=date(2025, 1, 1),
                    end_date=date(2025, 2, 1),
                ),
            )

        assert exc.value.status_code == 404


# ============================================================
# PATCH SEASON
# ============================================================

class TestPatchSeason:

    def test_partial_update(self, db_session, season):
        """
        PATCH behavior → only provided fields should be updated.
        """
        result = patch_season(
            db_session,
            season.id,
            SeasonUpdate(country="Italy"),  # only updating one field
        )

        # Updated field
        assert result.country == "Italy"

        # Unchanged field
        assert result.start_date == season.start_date

    def test_missing_season_raises_404(self, db_session):
        """
        PATCH on non-existent season → should raise 404.
        """
        with pytest.raises(HTTPException) as exc:
            patch_season(db_session, 999, SeasonUpdate(country="X"))

        assert exc.value.status_code == 404


# ============================================================
# DELETE SEASON
# ============================================================

class TestDeleteSeason:

    def test_hard_delete(self, db_session, season):
        """
        If no matches exist → season should be permanently deleted.
        """
        result = delete_season(db_session, season.id)

        # Check response message
        assert result == {"message": "Season deleted successfully"}

        # Ensure row is removed from DB
        assert db_session.get(Season, season.id) is None

    def test_delete_with_matches_raises_400(self, db_session, season):
        """
        If matches exist → deletion should be blocked.
        """
        # Create a dependent match
        match = Match(season_id=season.id)
        db_session.add(match)
        db_session.commit()

        with pytest.raises(HTTPException) as exc:
            delete_season(db_session, season.id)

        assert exc.value.status_code == 400

    def test_missing_season_raises_404(self, db_session):
        """
        Deleting non-existent season → should raise 404.
        """
        with pytest.raises(HTTPException) as exc:
            delete_season(db_session, 999)

        assert exc.value.status_code == 404