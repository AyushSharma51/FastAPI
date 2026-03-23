
BASE = "/matches"


# ============================================================
# PLAYER STATS ROUTES (FIXED)
# ============================================================

class TestPlayerStatsRoutes:

    def test_create_player_stats(self, client, player, match, teams):
        """
        Scenario: Valid player stats input
        Expectation: 201 created with correct data
        """
        t1, _ = teams

        resp = client.post(f"{BASE}/match-stats", json={
            "player_id": player.id,
            "match_id": match.id,   # ✅ FIX
            "team_id": t1.id,       # ✅ FIX
            "goals": 1,
            "assists": 0,
            "minutes_played": 90
        })

        assert resp.status_code == 201
        assert resp.json()["goals"] == 1


    def test_get_player_stats_list(self, client, player, match, teams):
        """
        Scenario: Stats exist
        Expectation: Returns list
        """
        t1, _ = teams

        client.post(f"{BASE}/match-stats", json={
            "player_id": player.id,
            "match_id": match.id,   # ✅ FIX
            "team_id": t1.id,       # ✅ FIX
            "goals": 1,
            "assists": 0,
            "minutes_played": 90
        })

        resp = client.get(f"{BASE}/match-stats")

        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


    def test_get_player_stat_by_id(self, client, player, match, teams):
        """
        Scenario: Valid stat ID
        Expectation: Returns stat
        """
        t1, _ = teams

        create = client.post(f"{BASE}/match-stats", json={
            "player_id": player.id,
            "match_id": match.id,   # ✅ FIX
            "team_id": t1.id,       # ✅ FIX
            "goals": 1,
            "assists": 0,
            "minutes_played": 90
        })

        stat_id = create.json()["id"]

        resp = client.get(f"{BASE}/match-stats/{stat_id}")

        assert resp.status_code == 200
        assert resp.json()["id"] == stat_id