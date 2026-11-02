import os
import sys

# Ensure backend modules are importable when running tests from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from cloud_providers.catalog_pricing import tiered_egress_cost


def test_calculate_endpoint_returns_expected_structure():
    client = app.test_client()
    payload = {"cpu": 2, "ram": 8, "storage": 100, "network_ingress_gb_month": 10, "network_egress_gb_month": 10, "backup": 50}
    res = client.post("/api/calculate", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    # Ensure providers exist and AWS has a positive total
    assert "aws" in data and "azure" in data and "gcp" in data and "kubernetes" in data and "onprem" in data
    assert data["aws"]["total"] >= 0
    assert data["azure"]["total"] > 0
    assert data["gcp"]["total"] > 0
    assert data["kubernetes"]["total"] > 0
    assert data["onprem"].get("currency") == "USD"
    # AWS selected instance exists for MVP
    assert "selected_instance" in data["aws"]
    si = data["aws"]["selected_instance"]
    assert si.get("sku")
    assert si.get("count") >= 1


def test_five_provider_network_breakdown_uses_scenario_gb_per_month():
    client = app.test_client()
    payload = {
        "cpu": 2,
        "ram": 8,
        "storage": 100,
        "network_ingress_gb_month": 500,
        "network_egress_gb_month": 100,
        "network_cross_region_gb_month": 100,
        "network_source_region": "us-east",
        "network_destination_region": "us-west",
        "backup": 50,
    }
    response = client.post("/api/calculate", json=payload)
    assert response.status_code == 200
    results = response.get_json()

    expected_egress = {"aws": 9.0, "azure": 8.7, "gcp": 8.5, "kubernetes": 3.0, "onprem": 2.0}
    expected_cross_region = {"aws": 2.0, "azure": 2.0, "gcp": 1.0, "kubernetes": 3.0, "onprem": 2.0}
    assert set(results) == set(expected_egress)
    for provider, expected in expected_egress.items():
        breakdown = results[provider]["breakdown"]
        assert breakdown["network_egress"] == expected
        assert breakdown["network_ingress"] == 0
        assert breakdown["network_cross_region"] == expected_cross_region[provider]
        assert results[provider]["network_transfer"]["source_region"] == "us-east"
        assert results[provider]["network_transfer"]["destination_region"] == "us-west"
        assert round(sum(breakdown.values()), 2) == results[provider]["total"]


def test_tiered_egress_rates_at_boundaries():
    assert tiered_egress_cost("aws", 10_000) == 900
    assert round(tiered_egress_cost("aws", 10_001), 3) == 900.085
    assert round(tiered_egress_cost("aws", 50_001), 2) == 4300.07
    assert round(tiered_egress_cost("azure", 10_000), 2) == 870
    assert round(tiered_egress_cost("gcp", 10_000), 2) == 850


def test_cross_region_transfer_requires_distinct_regions():
    client = app.test_client()
    payload = {
        "cpu": 2,
        "ram": 8,
        "storage": 0,
        "network_egress_gb_month": 0,
        "network_cross_region_gb_month": 10,
        "backup": 0,
    }
    missing_regions = client.post("/api/calculate", json=payload)
    same_region = client.post("/api/calculate", json={**payload, "network_source_region": "us-east-1", "network_destination_region": "us-east-1"})
    assert missing_regions.status_code == 400
    assert same_region.status_code == 400


def test_instance_count_scales_compute_but_not_scenario_totals():
    client = app.test_client()
    payload = {
        "cpu": 2,
        "ram": 8,
        "storage": 100,
        "network_egress_gb_month": 100,
        "backup": 50,
    }
    single = client.post("/api/calculate", json={**payload, "instance_count": 1}).get_json()
    triple = client.post("/api/calculate", json={**payload, "instance_count": 3}).get_json()

    for provider in ("aws", "azure", "gcp"):
        hourly = single[provider]["selected_instance"]["price_per_hour"]
        assert triple[provider]["breakdown"]["instance"] == round(hourly * 730 * 3, 2)
    for provider in ("aws", "azure", "gcp", "kubernetes", "onprem"):
        for component in ("storage", "network_egress", "network_cross_region", "backup"):
            if component in single[provider]["breakdown"]:
                assert triple[provider]["breakdown"][component] == single[provider]["breakdown"][component]


def test_legacy_network_mbps_is_converted_to_gb_per_month():
    client = app.test_client()
    response = client.post("/api/calculate", json={"cpu": 2, "ram": 8, "storage": 0, "network": 1, "backup": 0})
    assert response.status_code == 200
    assert response.get_json()["aws"]["breakdown"]["network_egress"] == 29.16


def test_undersized_match_is_rejected_instead_of_returning_a_small_sku():
    client = app.test_client()
    response = client.post("/api/calculate", json={"cpu": 1000, "ram": 1000, "storage": 0, "network_egress_gb_month": 0, "backup": 0})
    assert response.status_code == 422
    assert "No catalog instance meets" in response.get_json()["details"]


def test_undersized_manual_sku_is_rejected():
    client = app.test_client()
    response = client.post("/api/calculate", json={"cpu": 4, "ram": 16, "storage": 0, "network_egress_gb_month": 0, "backup": 0, "aws_sku": "t3.large"})
    assert response.status_code == 422
    assert "below the requested" in response.get_json()["details"]


def test_price_provenance_is_returned_and_marks_static_prices():
    client = app.test_client()
    response = client.get("/api/catalog")
    assert response.status_code == 200
    provenance = response.get_json()["price_provenance"]
    assert set(provenance) == {"aws", "azure", "gcp"}
    for item in provenance.values():
        assert item["region"] is None
        assert item["last_updated"] is None
        assert "Static" in item["source"]

    quote = client.post("/api/calculate", json={"cpu": 2, "ram": 8, "storage": 0, "network_egress_gb_month": 0, "backup": 0}).get_json()
    for provider in ("aws", "azure", "gcp", "kubernetes", "onprem"):
        assert quote[provider]["price_provenance"]["source"]


def test_contact_endpoint_is_registered_without_resend_secret(monkeypatch):
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    response = app.test_client().post("/api/contact", json={"name": "Test", "email": "test@example.com", "message": "Hello"})
    assert response.status_code == 503
    assert response.get_json()["error"] == "Contact service is not configured"
