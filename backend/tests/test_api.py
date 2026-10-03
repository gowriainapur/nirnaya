"""
Test Suite: FastAPI Endpoints Integration
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "Procurement Compass"
    assert data["sources_count"] > 0
    assert data["policy_chunks_count"] > 0

def test_sources_endpoint(client):
    res = client.get("/api/sources")
    assert res.status_code == 200
    sources = res.json()
    assert len(sources) >= 5
    assert any(s["authority_level"] == 1 for s in sources)
    assert any(s["is_synthetic"] is True for s in sources)

def test_rulesets_endpoint(client):
    res = client.get("/api/rulesets")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 2
    assert any(r["ruleset_id"] == "gfr_2017_updated_31_01_2026" for r in data)

def test_assess_endpoint_normal_purchase(client):
    payload = {
        "item_description": "Oscilloscope for electronics lab",
        "category": "goods",
        "estimated_value_inr": 48000.0,
        "tax_inclusive": True,
        "procurement_date": "2026-02-15",
        "gem_status": "unavailable_verified",
        "funding_source": "institute"
    }
    res = client.post("/api/assess", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["decision"]["status"] == "COMPLETE"
    assert data["decision"]["procurement_route"] == "direct_purchase"
    assert len(data["citations"]) > 0
    assert data["verification"]["verification_status"] == "passed"
    assert "assessment_id" in data

def test_assess_endpoint_needs_info(client):
    payload = {
        "item_description": "Chemical reagents",
        "category": "goods",
        "estimated_value_inr": None,
        "tax_inclusive": True,
        "procurement_date": "2026-02-15",
        "gem_status": "unavailable_verified"
    }
    res = client.post("/api/assess", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["decision"]["status"] == "NEEDS_INFO"
    assert "estimated_value_inr" in data["decision"]["missing_fields"]

def test_compare_endpoint(client):
    res = client.post("/api/compare", json={"ruleset_a": "gfr_2017_historical_original", "ruleset_b": "gfr_2017_updated_31_01_2026"})
    assert res.status_code == 200
    data = res.json()
    assert data["diff_count"] >= 4
    assert any(d["change_type"] == "THRESHOLD_INCREASED" for d in data["comparison"])

def test_what_if_endpoint(client):
    payload = {
        "base_input": {
            "item_description": "Spectrometer sample stage",
            "category": "goods",
            "estimated_value_inr": 45000.0,
            "tax_inclusive": True,
            "procurement_date": "2026-02-15",
            "gem_status": "unavailable_verified"
        },
        "variations": {
            "estimated_value_inr": 85000.0,
            "gem_status": "available_verified"
        }
    }
    res = client.post("/api/what-if", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["simulation_count"] == 3
    # Check that baseline was direct_purchase, and value increase changed to purchase_committee
    routes = [r["route"] for r in data["results"]]
    assert "direct_purchase" in routes
    assert "purchase_committee" in routes

def test_eval_endpoint_runs_live(client):
    res = client.post("/api/eval")
    assert res.status_code == 200
    data = res.json()
    assert data["golden_test_results"]["passed"] == 28
    assert data["golden_test_results"]["accuracy"] == 1.0
    assert "retrieval_benchmark" in data
    assert "hybrid" in data["retrieval_benchmark"]

def test_audit_endpoint(client):
    res = client.get("/api/audit?limit=5")
    assert res.status_code == 200
    data = res.json()
    assert "records" in data
