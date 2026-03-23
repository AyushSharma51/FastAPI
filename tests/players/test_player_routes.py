BASE = "/players"
TEAM_BASE = "/team-players"
STATS_BASE = "/player-stats"


# ============================================================
# PLAYER ROUTES
# ============================================================

class TestPlayerRoutes:

    def test_create_player(self, client):
        """
        Scenario: Valid player input
        Expectation: 201 created with correct data
        """
        resp = client.post(BASE, json={
            "name": "Messi",
            "birth_date": "1987-06-24",
            "nationality": "Argentina"
        })

        assert resp.status_code == 201
        assert resp.json()["name"] == "messi"  # normalized

    def test_get_all_players(self, client):
        """
        Scenario: No players initially
        Expectation: Empty list
        """
        resp = client.get(BASE)

        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_single_player(self, client):
        """
        Scenario: Player exists
        Expectation: Return correct player
        """
        create = client.post(BASE, json={
            "name": "Ronaldo",
            "birth_date": "1985-02-05",
            "nationality": "Portugal"
        })

        player_id = create.json()["id"]

        resp = client.get(f"{BASE}/{player_id}")

        assert resp.status_code == 200
        assert resp.json()["id"] == player_id

    def test_get_invalid_player(self, client):
        """
        Scenario: Player does not exist
        Expectation: 404 error
        """
        resp = client.get(f"{BASE}/99999")
        assert resp.status_code == 404

    def test_update_player(self, client):
        """
        Scenario: Full update (PUT)
        Expectation: Player data updated
        """
        create = client.post(BASE, json={
            "name": "Old",
            "birth_date": "1990-01-01",
            "nationality": "Old"
        })

        player_id = create.json()["id"]

        resp = client.put(f"{BASE}/{player_id}", json={
            "name": "New",
            "birth_date": "1995-01-01",
            "nationality": "New"
        })

        assert resp.status_code == 200
        assert resp.json()["name"] == "new"

    def test_patch_player(self, client):
        """
        Scenario: Partial update
        Expectation: Only provided field updated
        """
        create = client.post(BASE, json={
            "name": "Patch",
            "birth_date": "1990-01-01",
            "nationality": "X"
        })

        player_id = create.json()["id"]

        resp = client.patch(f"{BASE}/{player_id}", json={"name": "Updated"})

        assert resp.status_code == 200
        assert resp.json()["name"] == "updated"

    def test_delete_player(self, client):
        """
        Scenario: Valid delete
        Expectation: Player removed
        """
        create = client.post(BASE, json={
            "name": "Delete",
            "birth_date": "1990-01-01",
            "nationality": "X"
        })

        player_id = create.json()["id"]

        resp = client.delete(f"{BASE}/{player_id}")

        assert resp.status_code == 200


# ============================================================
# PLAYER CUMULATIVE STATS
# ============================================================

class TestPlayerCumulativeStats:

    def test_invalid_player(self, client):
        """
        Scenario: Player does not exist
        Expectation: 404 error
        """
        resp = client.get(f"{BASE}/99999/stats")
        assert resp.status_code == 404

    def test_valid_player_no_stats(self, client):
        """
        Scenario: Player exists but no stats
        Expectation: All values = 0
        """
        create = client.post(BASE, json={
            "name": "Stats",
            "birth_date": "1990-01-01",
            "nationality": "X"
        })

        player_id = create.json()["id"]

        resp = client.get(f"{BASE}/{player_id}/stats")

        assert resp.status_code == 200
        assert resp.json()["total_goals"] == 0


# ============================================================
# TEAM PLAYER ROUTES
# ============================================================

class TestTeamPlayerRoutes:

    def test_create_team_player(self, client, team, player, season):
        """
        Scenario: Valid roster entry
        Expectation: 201 created
        """
        resp = client.post(TEAM_BASE, json={
            "team_id": team.id,
            "player_id": player.id,
            "season_id": season.id,
            "jersey_number": 10
        })

        assert resp.status_code == 201
        assert resp.json()["team_id"] == team.id

    def test_get_team_player(self, client, team, player, season):
        """
        Scenario: Valid roster ID
        Expectation: Entry returned
        """
        create = client.post(TEAM_BASE, json={
            "team_id": team.id,
            "player_id": player.id,
            "season_id": season.id,
            "jersey_number": 10
        })

        tp_id = create.json()["id"]

        resp = client.get(f"{TEAM_BASE}/{tp_id}")

        assert resp.status_code == 200
        assert resp.json()["id"] == tp_id

    def test_patch_team_player(self, client, team, player, season):
        """
        Scenario: Update jersey number
        Expectation: Updated value returned
        """
        create = client.post(TEAM_BASE, json={
            "team_id": team.id,
            "player_id": player.id,
            "season_id": season.id,
            "jersey_number": 10
        })

        tp_id = create.json()["id"]

        resp = client.patch(f"{TEAM_BASE}/{tp_id}", json={"jersey_number": 7})

        assert resp.status_code == 200
        assert resp.json()["jersey_number"] == 7

    def test_delete_team_player(self, client, team, player, season):
        """
        Scenario: Valid delete
        Expectation: Entry removed
        """
        create = client.post(TEAM_BASE, json={
            "team_id": team.id,
            "player_id": player.id,
            "season_id": season.id,
            "jersey_number": 10
        })

        tp_id = create.json()["id"]

        resp = client.delete(f"{TEAM_BASE}/{tp_id}")

        assert resp.status_code == 200


# ============================================================
# PLAYER STATS ROUTES
# ============================================================

class TestPlayerStatsRoutes:

    def test_get_player_stat_invalid(self, client):
        """
        Scenario: Stat does not exist
        Expectation: 404 error
        """
        resp = client.get(f"{STATS_BASE}/99999")
        assert resp.status_code == 404

    def test_patch_player_stat_invalid(self, client):
        """
        Scenario: Stat does not exist
        Expectation: 404 error
        """
        resp = client.patch(f"{STATS_BASE}/99999", json={"goals": 2})
        assert resp.status_code == 404

    def test_delete_player_stat_invalid(self, client):
        """
        Scenario: Stat does not exist
        Expectation: 404 error
        """
        resp = client.delete(f"{STATS_BASE}/99999")
        assert resp.status_code == 404