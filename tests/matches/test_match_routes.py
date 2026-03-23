
from datetime import date

BASE = "/matches"


# ============================================================
# PLAYER STATS ROUTES
# ============================================================

class TestPlayerStatsRoutes:

    def test_create_player_stats(self, client, player):
        """
        Scenario: Valid player stats input
        Expectation: 201 created with correct data
        """
        resp = client.post(f"{BASE}/match-stats", json={
            "player_id": player.id,
            "match_id": 1,
            "team_id": 1,
            "goals": 1,
            "assists": 0,
            "minutes_played": 90
        })

        assert resp.status_code == 201
        assert resp.json()["goals"] == 1

    def test_get_player_stats_list(self, client, player):
        """
        Scenario: Stats exist
        Expectation: Returns list
        """
        client.post(f"{BASE}/match-stats", json={
            "player_id": player.id,
            "match_id": 1,
            "team_id": 1,
            "goals": 1,
            "assists": 0,
            "minutes_played": 90
        })

        resp = client.get(f"{BASE}/match-stats")

        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_player_stat_by_id(self, client, player):
        """
        Scenario: Valid stat ID
        Expectation: Returns stat
        """
        create = client.post(f"{BASE}/match-stats", json={
            "player_id": player.id,
            "match_id": 1,
            "team_id": 1,
            "goals": 1,
            "assists": 0,
            "minutes_played": 90
        })

        stat_id = create.json()["id"]

        resp = client.get(f"{BASE}/match-stats/{stat_id}")

        assert resp.status_code == 200
        assert resp.json()["id"] == stat_id


# ============================================================
# MATCH LIST
# ============================================================

class TestListMatches:

    def test_returns_empty(self, client):
        """
        Scenario: No matches exist
        Expectation: Empty list response
        """
        resp = client.get(BASE)

        assert resp.status_code == 200
        assert resp.json()["matches"] == []

    def test_returns_matches(self, client, season, teams):
        """
        Scenario: Match created
        Expectation: Appears in list
        """
        t1, t2 = teams

        client.post(BASE, json=[{
            "season_id": season.id,
            "venue": "Stadium",
            "date": str(date.today()),
            "status": "completed",
            "participants": [
                {"team_id": t1.id, "is_home": True},
                {"team_id": t2.id, "is_home": False}
            ]
        }])

        resp = client.get(BASE)

        assert resp.status_code == 200
        assert len(resp.json()["matches"]) == 1


# ============================================================
# GET MATCH BY ID
# ============================================================

class TestGetMatch:

    def test_valid_match(self, client, season, teams):
        """
        Scenario: Valid match ID
        Expectation: Match returned
        """
        t1, t2 = teams

        create = client.post(BASE, json=[{
            "season_id": season.id,
            "venue": "Stadium",
            "date": str(date.today()),
            "status": "completed",
            "participants": [
                {"team_id": t1.id, "is_home": True},
                {"team_id": t2.id, "is_home": False}
            ]
        }])

        match_id = create.json()[0]["id"]

        resp = client.get(f"{BASE}/{match_id}")

        assert resp.status_code == 200
        assert resp.json()["id"] == match_id

    def test_invalid_id(self, client):
        """
        Scenario: Non-existent match
        Expectation: 404 error
        """
        resp = client.get(f"{BASE}/99999")
        assert resp.status_code == 404


# ============================================================
# CREATE MATCH
# ============================================================

class TestCreateMatch:

    def test_valid_creation(self, client, season, teams):
        """
        Scenario: Valid input
        Expectation: Match created (201)
        """
        t1, t2 = teams

        resp = client.post(BASE, json=[{
            "season_id": season.id,
            "venue": "Stadium",
            "date": str(date.today()),
            "status": "completed",
            "participants": [
                {"team_id": t1.id, "is_home": True},
                {"team_id": t2.id, "is_home": False}
            ]
        }])

        assert resp.status_code == 201
        assert resp.json()[0]["venue"] == "stadium"

    def test_invalid_payload(self, client):
        """
        Scenario: Missing required fields
        Expectation: 422 validation error
        """
        resp = client.post(BASE, json=[{}])
        assert resp.status_code == 422


# ============================================================
# PATCH MATCH
# ============================================================

class TestPatchMatch:

    def test_partial_update(self, client, season, teams):
        """
        Scenario: Update only venue
        Expectation: Venue updated
        """
        t1, t2 = teams

        create = client.post(BASE, json=[{
            "season_id": season.id,
            "venue": "Old",
            "date": str(date.today()),
            "status": "completed",
            "participants": [
                {"team_id": t1.id, "is_home": True},
                {"team_id": t2.id, "is_home": False}
            ]
        }])

        match_id = create.json()[0]["id"]

        resp = client.patch(f"{BASE}/{match_id}", json={"venue": "New"})

        assert resp.status_code == 200
        assert resp.json()["venue"] == "new"

    def test_invalid_id(self, client):
        """
        Scenario: Invalid match ID
        Expectation: 404 error
        """
        resp = client.patch(f"{BASE}/99999", json={"venue": "X"})
        assert resp.status_code == 404


# ============================================================
# PUT MATCH
# ============================================================

class TestPutMatch:

    def test_full_replace(self, client, season, teams):
        """
        Scenario: Replace all fields
        Expectation: Data updated
        """
        t1, t2 = teams

        create = client.post(BASE, json=[{
            "season_id": season.id,
            "venue": "Old",
            "date": str(date.today()),
            "status": "completed",
            "participants": [
                {"team_id": t1.id, "is_home": True},
                {"team_id": t2.id, "is_home": False}
            ]
        }])

        match_id = create.json()[0]["id"]

        resp = client.put(f"{BASE}/{match_id}", json={
            "season_id": season.id,
            "venue": "New Venue",
            "date": str(date.today()),
            "status": "completed"
        })

        assert resp.status_code == 200
        assert resp.json()["venue"] == "new venue"


# ============================================================
# DELETE MATCH
# ============================================================

class TestDeleteMatch:

    def test_delete_success(self, client, season, teams):
        """
        Scenario: Valid delete
        Expectation: Match removed
        """
        t1, t2 = teams

        create = client.post(BASE, json=[{
            "season_id": season.id,
            "venue": "Stadium",
            "date": str(date.today()),
            "status": "completed",
            "participants": [
                {"team_id": t1.id, "is_home": True},
                {"team_id": t2.id, "is_home": False}
            ]
        }])

        match_id = create.json()[0]["id"]

        resp = client.delete(f"{BASE}/{match_id}")

        assert resp.status_code == 200
        assert resp.json()["id"] == match_id

    def test_invalid_id(self, client):
        """
        Scenario: Non-existent match
        Expectation: 404 error
        """
        resp = client.delete(f"{BASE}/99999")
        assert resp.status_code == 404