import pytest
from fastapi import HTTPException

from src.app.db_models import (
    Team,
    MatchParticipant,
    PlayerMatchStat,
    TeamPlayer,
)
from src.app.schemas.team_schemas import (
    TeamCreate,
    TeamUpdate,
    TeamPlayersCreate,
    TeamPlayersUpdate,
)
from src.app.schemas.common_schemas import PaginationParams
from src.app.services.team_services import (
    create_team,
    get_all_teams,
    get_team_by_id,
    update_team,
    patch_team,
    delete_team,
    create_team_players,
    get_team_player_by_id,
    update_team_player,
    delete_team_player,
    get_team_cumulative_stats,
)


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture()
def team(db_session):
    """Create a basic team"""
    t = Team(name="Barcelona", city="Barcelona", founded_year=1899, stadium="Camp Nou")
    db_session.add(t)
    db_session.commit()
    db_session.refresh(t)
    return t


@pytest.fixture()
def pagination():
    """Basic pagination object"""
    return PaginationParams(offset=0, limit=10)


# ============================================================
# TEAM CRUD
# ============================================================


class TestTeamCRUD:

    def test_create_team(self, db_session):
        """
        Scenario: Valid team input
        Expectation: Team should be created
        """
        result = create_team(
            db_session,
            TeamCreate(
                name="Real Madrid",
                city="Madrid",
                founded_year=1902,
                stadium="Bernabeu",
            ),
        )

        assert result.id is not None
        assert result.name == "Real Madrid"

    def test_get_all_teams(self, db_session, team, pagination):
        """
        Scenario: Team exists
        Expectation: Should return list of teams
        """
        result = get_all_teams(db_session, pagination)

        assert len(result) == 1
        assert result[0].id == team.id

    def test_get_team_by_id(self, db_session, team):
        """
        Scenario: Valid ID
        Expectation: Team returned
        """
        result = get_team_by_id(db_session, team.id)
        assert result.id == team.id

    def test_get_team_invalid_id(self, db_session):
        """
        Scenario: Invalid ID
        Expectation: 404 error
        """
        with pytest.raises(HTTPException):
            get_team_by_id(db_session, 999)

    def test_update_team(self, db_session, team):
        """
        Scenario: Full update (PUT)
        Expectation: All fields updated
        """
        result = update_team(
            db_session,
            team.id,
            TeamCreate(
                name="Updated",
                city="New City",
                founded_year=2000,
                stadium="New Stadium",
            ),
        )

        assert result.name == "Updated"

    def test_patch_team(self, db_session, team):
        """
        Scenario: Partial update (PATCH)
        Expectation: Only provided fields updated
        """
        result = patch_team(
            db_session,
            team.id,
            TeamUpdate(name="Patched Name"),
        )

        assert result.name == "Patched Name"

    def test_delete_team_success(self, db_session, team):
        """
        Scenario: No match dependency
        Expectation: Team deleted
        """
        result = delete_team(db_session, team.id)

        assert result["message"] == "Team deleted successfully"
        assert db_session.get(Team, team.id) is None

    def test_delete_team_with_match_dependency(self, db_session, team, match):
        """
        Scenario: Team is used in match
        Expectation: deletion blocked
        """

        # Clear existing participants (optional but safe)
        db_session.query(MatchParticipant).delete()

        mp1 = MatchParticipant(match_id=match.id, team_id=team.id, is_home=True)
        mp2 = MatchParticipant(match_id=match.id, team_id=team.id, is_home=False)

        db_session.add_all([mp1, mp2])
        db_session.commit()

        with pytest.raises(HTTPException) as exc:
            delete_team(db_session, team.id)

        assert exc.value.status_code == 400

# ============================================================
# TEAM PLAYER (ROSTER)
# ============================================================


class TestTeamPlayer:

    def test_create_team_player(self, db_session, team, player, season):
        """
        Scenario: Valid roster entry
        Expectation: Entry created
        """
        tp = create_team_players(
            db_session,
            TeamPlayersCreate(
                team_id=team.id,
                player_id=player.id,
                season_id=season.id,
                jersey_number=10,
            ),
        )

        assert tp.id is not None

    def test_get_team_player_by_id(self, db_session, team, player, season):
        """
        Scenario: Valid roster ID
        Expectation: Entry returned
        """
        tp = TeamPlayer(
            team_id=team.id, player_id=player.id, season_id=season.id, jersey_number=10
        )
        db_session.add(tp)
        db_session.commit()

        result = get_team_player_by_id(db_session, tp.id)
        assert result.id == tp.id

    def test_update_team_player(self, db_session, team, player, season):
        """
        Scenario: Partial update
        Expectation: Fields updated
        """
        tp = TeamPlayer(
            team_id=team.id, player_id=player.id, season_id=season.id, jersey_number=10
        )
        db_session.add(tp)
        db_session.commit()
        db_session.refresh(tp)

        result = update_team_player(
            db_session, tp.id, TeamPlayersUpdate(season_id=season.id)
        )

        assert result.season_id == season.id

    def test_delete_team_player_success(self, db_session, team, player, season):
        """
        Scenario: No stats dependency
        Expectation: Entry deleted
        """
        tp = TeamPlayer(
            team_id=team.id, player_id=player.id, season_id=season.id, jersey_number=10
        )
        db_session.add(tp)
        db_session.commit()

        result = delete_team_player(db_session, tp.id)

        assert result["message"] == "Roster entry deleted"

    def test_delete_team_player_with_stats(self, db_session,match, team, player, season):
        """
        Scenario: Player has match stats
        Expectation: Deletion blocked (400)
        """
        tp = TeamPlayer(
            team_id=team.id, player_id=player.id, season_id=season.id, jersey_number=10
        )
        db_session.add(tp)
        db_session.commit()

        stat = PlayerMatchStat(
           match_id=match.id, player_id=player.id, team_id=team.id, goals=0, assists=0, minutes_played=0
        )
        db_session.add(stat)
        db_session.commit()

        with pytest.raises(HTTPException) as exc:
            delete_team_player(db_session, tp.id)

        assert exc.value.status_code == 400


# ============================================================
# TEAM CUMULATIVE STATS
# ============================================================


class TestTeamCumulativeStats:

    def test_invalid_team_raises_404(self, db_session):
        """
        Scenario: Team does not exist
        Expectation: 404 error
        """
        with pytest.raises(HTTPException):
            get_team_cumulative_stats(db_session, 999)

    def test_returns_zero_stats(self, db_session, team):
        """
        Scenario: Team exists but no matches
        Expectation: All stats should be 0
        """
        result = get_team_cumulative_stats(db_session, team.id)

        assert result["matches_played"] == 0
        assert result["points"] == 0
