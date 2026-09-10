import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "RxDecoder" in data["app"]

def test_list_samples():
    response = client.get("/api/samples")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3
    sample_ids = [s["id"] for s in data]
    assert "sample_handwritten_amoxicillin" in sample_ids

def test_decode_sample_endpoint():
    payload = {"sample_id": "sample_handwritten_amoxicillin"}
    response = client.post("/api/decode/sample", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["medications"]) >= 2
    assert data["medications"][0]["name"] == "Amoxicillin"
    assert data["phi_report"]["sanitized"] is True
    assert len(data["checklist"]) >= 2

def test_pharmacy_search_endpoint():
    response = client.get("/api/pharmacies?lat=37.7749&lon=-122.4194")
    assert response.status_code == 200
    data = response.json()
    assert "pharmacies" in data
    assert len(data["pharmacies"]) > 0
    assert "google_maps_url" in data["pharmacies"][0]
