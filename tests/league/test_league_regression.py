"""
Regression tests for the League feature
────────────────────────────────────────
Rule: add a test here ONLY when a real bug is found and fixed.
      Each test must reference the bug/ticket that caused it.
      Do NOT duplicate scenarios already covered in test_league_services.py
      or test_league_routes.py.

Currently guarding
  R03 – PATCH /league/0 must be rejected (Path ge=1 constraint)
         Unique: neither services nor routes tests exercise id=0 specifically.
  R10 – PATCH response must include `id` (from_attributes ORM mode)
         Unique: guards against a broken schema change dropping the field.
"""

BASE = "/league"


# ── R03 ─────────────────────────────────────────────────────────────────────
class TestR03_PatchIdZeroRejected:
    def test_patch_id_zero_is_422(self, client):
        resp = client.patch(f"{BASE}/0", json={"name": "X"})
        assert (
            resp.status_code == 422
        ), "R03: PATCH /league/0 should be rejected by Path(ge=1)"


# ── R10 ─────────────────────────────────────────────────────────────────────
class TestR10_UpdateResponseIncludesId:
    def test_id_present_in_patch_response(self, client, league_in_db):
        resp = client.patch(f"{BASE}/{league_in_db.id}", json={"name": "Updated"})
        body = resp.json()
        assert (
            "id" in body
        ), "R10: PATCH response missing 'id' — from_attributes may be misconfigured"
        assert body["id"] == league_in_db.id
