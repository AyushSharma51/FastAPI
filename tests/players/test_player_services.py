import pytest
from datetime import date
from fastapi import HTTPException

from src.app.db_models import (
    Player,
    PlayerMatchStat,

)
from src.app.schemas.player_schemas import (
    PlayerCreate,
    PlayerUpdate,
    PlayerMatchStatsCreate,
    PlayerMatchStatsUpdate,
)
from src.app.schemas.common_schemas import PaginationParams
from src.app.services.player_services import (
    get_all_players,
    create_a_player,
    get_player_by_id,
    update_player,
    patch_player,
    delete_player,
    create_player_stats,
    list_player_stats,
    get_player_cumulative_stats,
    get_player_stat_by_id,
    update_player_stat,
    delete_player_stat,
)


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture()
def player(db_session):
    """Create a basic player"""
    p = Player(name="Messi", birth_date=date(1987, 6, 24), nationality="Argentina")
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return p


@pytest.fixture()
def pagination():
    """Basic pagination object"""
    return PaginationParams(offset=0, limit=10)


# ============================================================
# PLAYER CRUD
# ============================================================

class TestPlayerCRUD:

    def test_create_player(self, db_session):
        """
        Scenario: Valid player data
        Expectation: Player should be created in DB
        """
        result = create_a_player(
            db_session,
            PlayerCreate(name="Ronaldo", birth_date=date(1985, 2, 5), nationality="Portugal"),
        )

        assert result.id is not None
        assert result.name == "Ronaldo"

    def test_get_all_players(self, db_session, player, pagination):
        """
        Scenario: Player exists
        Expectation: Should return list with player
        """
        result = get_all_players(db_session, pagination)

        assert len(result) == 1
        assert result[0].id == player.id

    def test_get_player_by_id(self, db_session, player):
        """
        Scenario: Valid ID
        Expectation: Correct player returned
        """
        result = get_player_by_id(db_session, player.id)
        assert result.id == player.id

    def test_get_player_invalid_id(self, db_session):
        """
        Scenario: Invalid ID
        Expectation: 404 error
        """
        with pytest.raises(HTTPException):
            get_player_by_id(db_session, 999)

    def test_update_player(self, db_session, player):
        """
        Scenario: Full update (PUT)
        Expectation: All fields updated
        """
        result = update_player(
            db_session,
            player.id,
            PlayerCreate(name="Neymar", birth_date=date(1992, 2, 5), nationality="Brazil"),
        )

        assert result.name == "Neymar"

    def test_patch_player(self, db_session, player):
        """
        Scenario: Partial update (PATCH)
        Expectation: Only provided fields updated
        """
        result = patch_player(
            db_session,
            player.id,
            PlayerUpdate(name="Updated Name"),
        )

        assert result.name == "Updated Name"

    def test_delete_player_success(self, db_session, player):
        """
        Scenario: No dependencies
        Expectation: Player deleted
        """
        result = delete_player(db_session, player.id)

        assert result["message"] == "Player deleted successfully"
        assert db_session.get(Player, player.id) is None

    def test_delete_player_with_dependencies(self, db_session, player):
        """
        Scenario: Player has stats or team
        Expectation: Deletion blocked (400)
        """
        stat = PlayerMatchStat(player_id=player.id)
        db_session.add(stat)
        db_session.commit()

        with pytest.raises(HTTPException) as exc:
            delete_player(db_session, player.id)

        assert exc.value.status_code == 400


# ============================================================
# PLAYER MATCH STATS
# ============================================================

class TestPlayerMatchStats:

    def test_create_player_stats(self, db_session, player):
        """
        Scenario: Valid stats input
        Expectation: Stats created
        """
        stat = create_player_stats(
            db_session,
            PlayerMatchStatsCreate(
                player_id=player.id,
                match_id=1,
                team_id=1,
                goals=1,
                assists=0,
                minutes_played=90,
            ),
        )

        assert stat.id is not None
        assert stat.goals == 1

    def test_list_player_stats(self, db_session, player, pagination):
        """
        Scenario: Stats exist
        Expectation: Should return list
        """
        stat = PlayerMatchStat(player_id=player.id)
        db_session.add(stat)
        db_session.commit()

        result = list_player_stats(db_session, pagination)

        assert len(result) >= 1

    def test_get_stat_by_id(self, db_session, player):
        """
        Scenario: Valid stat ID
        Expectation: Stat returned
        """
        stat = PlayerMatchStat(player_id=player.id)
        db_session.add(stat)
        db_session.commit()

        result = get_player_stat_by_id(db_session, stat.id)
        assert result.id == stat.id

    def test_update_stat(self, db_session, player):
        """
        Scenario: Partial update of stat
        Expectation: Fields updated
        """
        stat = PlayerMatchStat(player_id=player.id, goals=1)
        db_session.add(stat)
        db_session.commit()

        result = update_player_stat(
            db_session,
            stat.id,
            PlayerMatchStatsUpdate(goals=5),
        )

        assert result.goals == 5

    def test_delete_stat(self, db_session, player):
        """
        Scenario: Valid delete
        Expectation: Stat removed
        """
        stat = PlayerMatchStat(player_id=player.id)
        db_session.add(stat)
        db_session.commit()

        result = delete_player_stat(db_session, stat.id)

        assert result["message"] == "Player stat deleted successfully"
        assert db_session.get(PlayerMatchStat, stat.id) is None


# ============================================================
# CUMULATIVE STATS
# ============================================================

class TestCumulativeStats:

    def test_invalid_player_raises_404(self, db_session):
        """
        Scenario: Player does not exist
        Expectation: 404 error
        """
        with pytest.raises(HTTPException):
            get_player_cumulative_stats(db_session, 999)

    def test_returns_zero_stats(self, db_session, player):
        """
        Scenario: Player exists but no stats
        Expectation: All values should be 0
        """
        result = get_player_cumulative_stats(db_session, player.id)

        assert result["total_goals"] == 0
        assert result["matches_played"] == 0