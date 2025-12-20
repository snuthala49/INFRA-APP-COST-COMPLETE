import os
import sys

# Ensure backend modules are importable when running tests from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app


def test_calculate_endpoint_returns_expected_structure():
    client = app.test_client()
    payload = {"cpu": 2, "ram": 8, "storage": 100, "network": 10, "backup": 50}
    res = client.post("/calculate", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    # Ensure providers exist and AWS has a positive total
    assert "aws" in data and "azure" in data and "gcp" in data and "kubernetes" in data and "onprem" in data
    assert data["aws"]["total"] >= 0
    assert data["azure"]["total"] > 0
    assert data["gcp"]["total"] > 0
    assert data["kubernetes"]["total"] > 0
    assert data["onprem"].get("currency") == "USD"
