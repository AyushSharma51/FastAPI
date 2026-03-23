

BASE = "/teams"


# ============================================================
# GET TEAM
# ============================================================

class TestGetTeam:

    def test_valid_team(self, client, team):
        """
        Scenario: Team exists
        Expectation: Return correct team
        """
        resp = client.get(f"{BASE}/{team.id}")

        assert resp.status_code == 200
        assert resp.json()["id"] == team.id

    def test_invalid_team(self, client):
        """
        Scenario: Team does not exist
        Expectation: 404 error
        """
        resp = client.get(f"{BASE}/99999")
        assert resp.status_code == 404


# ============================================================
# LIST TEAMS
# ============================================================

class TestListTeams:

    def test_returns_empty(self, client):
        """
        Scenario: No teams exist
        Expectation: Empty list
        """
        resp = client.get(BASE)

        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_returns_teams(self, client):
        """
        Scenario: Team exists
        Expectation: Appears in list
        """
        client.post(BASE, json={
            "name": "Barcelona",
            "city": "Barcelona",
            "founded_year": 1899,
            "stadium": "Camp Nou"
        })

        resp = client.get(BASE)

        assert resp.status_code == 200
        assert len(resp.json()) == 1


# ============================================================
# CREATE TEAM
# ============================================================

class TestCreateTeam:

    def test_valid_creation(self, client):
        """
        Scenario: Valid input
        Expectation: Team created (201)
        """
        resp = client.post(BASE, json={
            "name": "Real Madrid",
            "city": "Madrid",
            "founded_year": 1902,
            "stadium": "Bernabeu"
        })

        assert resp.status_code == 201
        assert resp.json()["name"] == "Real Madrid"

    def test_invalid_payload(self, client):
        """
        Scenario: Missing required fields
        Expectation: 422 validation error
        """
        resp = client.post(BASE, json={})
        assert resp.status_code == 422


# ============================================================
# UPDATE TEAM (PUT)
# ============================================================

class TestUpdateTeam:

    def test_valid_update(self, client):
        """
        Scenario: Replace team data
        Expectation: Updated values returned
        """
        create = client.post(BASE, json={
            "name": "Old",
            "city": "City",
            "founded_year": 1900,
            "stadium": "Old Stadium"
        })

        team_id = create.json()["id"]

        resp = client.put(f"{BASE}/{team_id}", json={
            "name": "New",
            "city": "New City",
            "founded_year": 2000,
            "stadium": "New Stadium"
        })

        assert resp.status_code == 200
        assert resp.json()["name"] == "New"

    def test_invalid_id(self, client):
        """
        Scenario: Team does not exist
        Expectation: 404 error
        """
        resp = client.put(f"{BASE}/99999", json={
            "name": "X",
            "city": "X",
            "founded_year": 1900,
            "stadium": "X"
        })

        assert resp.status_code == 404


# ============================================================
# PATCH TEAM
# ============================================================

class TestPatchTeam:

    def test_partial_update(self, client):
        """
        Scenario: Update only name
        Expectation: Field updated
        """
        create = client.post(BASE, json={
            "name": "Old",
            "city": "City",
            "founded_year": 1900,
            "stadium": "Stadium"
        })

        team_id = create.json()["id"]

        resp = client.patch(f"{BASE}/{team_id}", json={"name": "Updated"})

        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated"

    def test_invalid_id(self, client):
        """
        Scenario: Team does not exist
        Expectation: 404 error
        """
        resp = client.patch(f"{BASE}/99999", json={"name": "X"})
        assert resp.status_code == 404


# ============================================================
# DELETE TEAM
# ============================================================

class TestDeleteTeam:

    def test_delete_success(self, client):
        """
        Scenario: Valid delete
        Expectation: Team removed
        """
        create = client.post(BASE, json={
            "name": "Delete",
            "city": "City",
            "founded_year": 1900,
            "stadium": "Stadium"
        })

        team_id = create.json()["id"]

        resp = client.delete(f"{BASE}/{team_id}")

        assert resp.status_code == 200

    def test_invalid_id(self, client):
        """
        Scenario: Team does not exist
        Expectation: 404 error
        """
        resp = client.delete(f"{BASE}/99999")
        assert resp.status_code == 404


# ============================================================
# TEAM CUMULATIVE STATS
# ============================================================

class TestTeamStats:

    def test_invalid_team(self, client):
        """
        Scenario: Team does not exist
        Expectation: 404 error
        """
        resp = client.get(f"{BASE}/99999/stats")
        assert resp.status_code == 404

    def test_valid_team_no_stats(self, client):
        """
        Scenario: Team exists but no matches
        Expectation: All values = 0
        """
        create = client.post(BASE, json={
            "name": "Stats",
            "city": "City",
            "founded_year": 1900,
            "stadium": "Stadium"
        })

        team_id = create.json()["id"]

        resp = client.get(f"{BASE}/{team_id}/stats")

        assert resp.status_code == 200
        assert resp.json()["matches_played"] == 0