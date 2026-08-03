from __future__ import annotations

from fastapi.testclient import TestClient

from services.api.app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_city_contract() -> None:
    response = client.get("/v1/city")
    assert response.status_code == 200
    payload = response.json()
    assert payload["grid"] == {"rows": 6, "columns": 8}
    assert len(payload["zones"]) == 48
    assert payload["data_status"] == "synthetic demonstration data"


def test_scenario_contract() -> None:
    response = client.post(
        "/v1/scenarios/simulate",
        json={"zone_id": "Z30", "intervention": "tree_canopy", "coverage_fraction": 0.25},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["cooling_c"] >= 0
    assert payload["cost_crore"] > 0


def test_unknown_zone_returns_404() -> None:
    response = client.get("/v1/zones/Z99")
    assert response.status_code == 404


def test_optimizer_contract() -> None:
    response = client.post(
        "/v1/portfolios/optimize",
        json={"budget_crore": 60, "max_items_per_zone": 2},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["committed_crore"] <= 60
    assert payload["items"]
