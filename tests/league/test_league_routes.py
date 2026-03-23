"""
Integration tests for /league routes
─────────────────────────────────────
Owns: HTTP contract only — status codes, response shape, input validation.
Does NOT re-test business logic already covered in test_league_services.py.
The rule: if removing the DB and mocking the service would still let the
test pass, it belongs here. If it needs real SQL, it belongs in services.
"""

BASE = "/league"


class TestGetLeagues:

    def test_returns_200_and_list(self, client):
        resp = client.get(BASE)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
      

    def test_response_shape(self, client, league_in_db):
        resp = client.get(BASE)
        item=resp.json()[0]
        assert set(item.keys()) == {"id", "name"}  # no extra fields leaked


class TestCreateLeague:

    def test_returns_201_with_id_and_name(self, client):
        resp = client.post(BASE, json={"name": "Bundesliga"})
        assert resp.status_code == 201
        assert "id" in resp.json()
        assert resp.json()["name"] == "Bundesliga"

    def test_missing_name_returns_422(self, client):
        resp = client.post(BASE, json={})
        assert resp.status_code == 422

    def test_duplicate_name_returns_409(self, client, league_in_db):
        resp = client.post(BASE, json={"name": league_in_db.name})
        assert resp.status_code == 409
        assert "already exists" in resp.json()["detail"]


class TestUpdateLeague:

    def test_returns_200_with_updated_name(self, client, league_in_db):
        resp = client.patch(f"{BASE}/{league_in_db.id}", json={"name": "EPL"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "EPL"
        assert resp.json()["id"] == league_in_db.id

    def test_same_name_returns_409(self, client, league_in_db, league_with_season):
        resp = client.patch(f"{BASE}/{league_in_db.id}", json={"name":"La Liga"})
        assert resp.status_code == 409

    def test_nonexistent_returns_404(self, client):
        assert client.patch(f"{BASE}/99999", json={"name": "X"}).status_code == 404

    def test_string_id_returns_422(self, client):
        assert client.patch(f"{BASE}/abc", json={"name": "X"}).status_code == 422

    def test_id_zero_returns_422(self, client):
        assert client.patch(f"{BASE}/0", json={"name": "X"}).status_code == 422


class TestDeleteLeague:

    def test_hard_delete_returns_200(self, client, league_in_db):
        resp = client.delete(f"{BASE}/{league_in_db.id}")
        assert resp.status_code == 200
        assert "permanently deleted" in resp.json()["message"]

    def test_soft_delete_returns_200(self, client, league_with_season):
        league, _ = league_with_season
        resp = client.delete(f"{BASE}/{league.id}")
        assert resp.status_code == 200
        assert "soft deleted" in resp.json()["message"]

    def test_nonexistent_returns_404(self, client):
        assert client.delete(f"{BASE}/99999").status_code == 404
