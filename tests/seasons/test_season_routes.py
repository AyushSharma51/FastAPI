
BASE = "/seasons"


# ============================================================
# LIST SEASONS
# ============================================================

class TestListSeasons:

    def test_returns_empty_list(self, client):
        """
        Scenario: No seasons exist
        Expectation: Empty list returned
        """
        resp = client.get(BASE)

        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_seasons(self, client, league):
        """
        Scenario: Season exists
        Expectation: Season appears in list
        """
        client.post(BASE, json={
            "league_id": league.id,
            "country": "England",
            "start_date": "2025-08-01",
            "end_date": "2026-05-31"
        })

        resp = client.get(BASE)

        assert resp.status_code == 200
        assert len(resp.json()) == 1


# ============================================================
# CREATE SEASON
# ============================================================

class TestCreateSeason:

    def test_valid_creation(self, client, league):
        """
        Scenario: Valid input
        Expectation: Season created (201)
        """
        resp = client.post(BASE, json={
            "league_id": league.id,
            "country": "Spain",
            "start_date": "2025-08-01",
            "end_date": "2026-05-31"
        })

        assert resp.status_code == 201
        assert resp.json()["country"] == "Spain"

    def test_invalid_league_returns_404(self, client):
        """
        Scenario: Invalid league_id
        Expectation: 404 error
        """
        resp = client.post(BASE, json={
            "league_id": 999,
            "country": "Spain",
            "start_date": "2025-08-01",
            "end_date": "2026-05-31"
        })

        assert resp.status_code == 404

    def test_invalid_payload_returns_422(self, client):
        """
        Scenario: Missing required fields
        Expectation: 422 validation error
        """
        resp = client.post(BASE, json={})
        assert resp.status_code == 422


# ============================================================
# UPDATE SEASON (PUT)
# ============================================================

class TestUpdateSeason:

    def test_valid_update(self, client, league):
        """
        Scenario: Valid season update
        Expectation: Data replaced
        """
        create = client.post(BASE, json={
            "league_id": league.id,
            "country": "Old",
            "start_date": "2025-08-01",
            "end_date": "2026-05-31"
        })

        season_id = create.json()["id"]

        resp = client.put(f"{BASE}/{season_id}", json={
            "league_id": league.id,
            "country": "Updated",
            "start_date": "2026-01-01",
            "end_date": "2026-12-01"
        })

        assert resp.status_code == 200
        assert resp.json()["country"] == "Updated"

    def test_invalid_id_returns_404(self, client, league):
        """
        Scenario: Season does not exist
        Expectation: 404 error
        """
        resp = client.put(f"{BASE}/99999", json={
            "league_id": league.id,
            "country": "X",
            "start_date": "2025-01-01",
            "end_date": "2025-12-01"
        })

        assert resp.status_code == 404


# ============================================================
# PATCH SEASON
# ============================================================

class TestPatchSeason:

    def test_partial_update(self, client, league):
        """
        Scenario: Update only country
        Expectation: Field updated
        """
        create = client.post(BASE, json={
            "league_id": league.id,
            "country": "Old",
            "start_date": "2025-08-01",
            "end_date": "2026-05-31"
        })

        season_id = create.json()["id"]

        resp = client.patch(f"{BASE}/{season_id}", json={
            "country": "New"
        })

        assert resp.status_code == 200
        assert resp.json()["country"] == "New"

    def test_invalid_id_returns_404(self, client):
        """
        Scenario: Season does not exist
        Expectation: 404 error
        """
        resp = client.patch(f"{BASE}/99999", json={"country": "X"})
        assert resp.status_code == 404


# ============================================================
# DELETE SEASON
# ============================================================

class TestDeleteSeason:

    def test_delete_success(self, client, league):
        """
        Scenario: No dependencies
        Expectation: Season deleted
        """
        create = client.post(BASE, json={
            "league_id": league.id,
            "country": "England",
            "start_date": "2025-08-01",
            "end_date": "2026-05-31"
        })

        season_id = create.json()["id"]

        resp = client.delete(f"{BASE}/{season_id}")

        assert resp.status_code == 200

    def test_invalid_id_returns_404(self, client):
        """
        Scenario: Season does not exist
        Expectation: 404 error
        """
        resp = client.delete(f"{BASE}/99999")
        assert resp.status_code == 404