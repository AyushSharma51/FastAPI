import pytest
from datetime import date
from fastapi import HTTPException

from src.app.db_models import (
    Match,
)
from src.app.schemas.match_schemas import MatchCreate
from src.app.services.match_services import (
    create_a_new_match,
    get_match_by_id,
    update_a_match,
    replace_a_match,
    delete_a_match,
)


# ============================================================
# NOTE:
# Using fixtures from conftest.py:
# - db_session
# - season
# - teams
# - match
# ============================================================


# ============================================================
# CREATE MATCH
# ============================================================

class TestCreateMatch:

    def test_creates_match_successfully(self, db_session, season, teams):
        """
        Scenario: Valid season + two valid teams
        Expectation: Match and participants should be created
        """
        t1, t2 = teams

        payload = [
            MatchCreate(
                season_id=season.id,
                venue="Arena",
                date=date(2025, 9, 1),
                status="scheduled",
                participants=[
                    {"team_id": t1.id, "is_home": True},
                    {"team_id": t2.id, "is_home": False},
                ],
            )
        ]

        result = create_a_new_match(db_session, payload)

        assert len(result) == 1
        assert result[0].venue == "Arena"

    def test_invalid_season_raises_404(self, db_session, teams):
        """
        Scenario: Season does not exist
        Expectation: 404 error
        """
        t1, t2 = teams

        with pytest.raises(HTTPException) as exc:
            create_a_new_match(
                db_session,
                [
                    MatchCreate(
                        season_id=999,
                        venue="Arena",
                        date=date(2025, 9, 1),
                        status="scheduled",
                        participants=[
                            {"team_id": t1.id, "is_home": True},
                            {"team_id": t2.id, "is_home": False},
                        ],
                    )
                ],
            )

        assert exc.value.status_code == 404

    def test_invalid_team_raises_404(self, db_session, season):
        """
        Scenario: One team does not exist
        Expectation: 404 error
        """
        with pytest.raises(HTTPException) as exc:
            create_a_new_match(
                db_session,
                [
                    MatchCreate(
                        season_id=season.id,
                        venue="Arena",
                        date=date(2025, 9, 1),
                        status="scheduled",
                        participants=[
                            {"team_id": 1, "is_home": True},
                            {"team_id": 999, "is_home": False},
                        ],
                    )
                ],
            )

        assert exc.value.status_code == 404

    def test_not_two_participants_raises_400(self, db_session, season, teams):
        """
        Scenario: Less than 2 teams provided
        Expectation: 400 error
        """
        t1, _ = teams

        with pytest.raises(HTTPException) as exc:
            create_a_new_match(
                db_session,
                [
                    MatchCreate(
                        season_id=season.id,
                        venue="Arena",
                        date=date(2025, 9, 1),
                        status="scheduled",
                        participants=[
                            {"team_id": t1.id, "is_home": True},
                        ],
                    )
                ],
            )

        assert exc.value.status_code == 400


# ============================================================
# GET MATCH BY ID
# ============================================================

class TestGetMatchById:

    def test_returns_match(self, db_session, match):
        """
        Scenario: Valid match ID
        Expectation: Match should be returned
        """
        result = get_match_by_id(db_session, match.id)

        assert result.id == match.id

    def test_invalid_id_raises_404(self, db_session):
        """
        Scenario: Match does not exist
        Expectation: 404 error
        """
        with pytest.raises(HTTPException):
            get_match_by_id(db_session, 999)


# ============================================================
# UPDATE MATCH (PATCH)
# ============================================================

class TestUpdateMatch:

    def test_updates_fields(self, db_session, match):
        """
        Scenario: Partial update
        Expectation: Only provided fields updated
        """
        class DummyUpdate:
            def model_dump(self, exclude_unset=True):
                return {"venue": "New Venue"}

        result = update_a_match(db_session, match.id, DummyUpdate())

        assert result.venue == "New Venue"

    def test_invalid_id_raises_404(self, db_session):
        """
        Scenario: Match does not exist
        Expectation: 404 error
        """
        with pytest.raises(HTTPException):
            update_a_match(db_session, 999, None)


# ============================================================
# REPLACE MATCH (PUT)
# ============================================================

class TestReplaceMatch:

    def test_replaces_match(self, db_session, match):
        """
        Scenario: Full replacement
        Expectation: All fields updated
        """
        class Dummy:
            venue = "New"
            date = date(2026, 1, 1)
            status = type("x", (), {"value": "completed"})

        result = replace_a_match(db_session, match.id, Dummy())

        assert result.venue == "New"

    def test_invalid_id_raises_404(self, db_session):
        """
        Scenario: Match does not exist
        Expectation: 404 error
        """
        with pytest.raises(HTTPException):
            replace_a_match(db_session, 999, None)


# ============================================================
# DELETE MATCH
# ============================================================

class TestDeleteMatch:

    def test_deletes_match(self, db_session, match):
        """
        Scenario: Valid delete
        Expectation: Match removed from DB
        """
        result = delete_a_match(db_session, match.id)

        assert result.id == match.id
        assert db_session.get(Match, match.id) is None

    def test_invalid_id_raises_404(self, db_session):
        """
        Scenario: Match does not exist
        Expectation: 404 error
        """
        with pytest.raises(HTTPException):
            delete_a_match(db_session, 999)