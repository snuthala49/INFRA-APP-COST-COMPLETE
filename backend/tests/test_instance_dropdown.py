import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app


def _payload(**overrides):
    payload = {
        "cpu": 4,
        "ram": 16,
        "storage": 200,
        "network": 20,
        "backup": 80,
    }
    payload.update(overrides)
    return payload


def test_aws_sku_override():
    client = app.test_client()
    res = client.post("/calculate", json=_payload(aws_sku="m6i.xlarge"))
    assert res.status_code == 200
    data = res.get_json()
    assert data["aws"]["selected_instance"]["sku"] == "m6i.xlarge"


def test_reserved_pricing():
    client = app.test_client()
    on_demand = client.post("/calculate", json=_payload(aws_sku="m6i.xlarge", pricing_model="on_demand")).get_json()
    reserved = client.post("/calculate", json=_payload(aws_sku="m6i.xlarge", pricing_model="reserved_1yr")).get_json()

    assert reserved["aws"]["breakdown"]["instance"] < on_demand["aws"]["breakdown"]["instance"]


def test_instance_count_multiplier():
    client = app.test_client()
    single = client.post("/calculate", json=_payload(aws_sku="m6i.xlarge", instance_count=1)).get_json()
    triple = client.post("/calculate", json=_payload(aws_sku="m6i.xlarge", instance_count=3)).get_json()

    assert round(triple["aws"]["breakdown"]["instance"], 2) == round(single["aws"]["breakdown"]["instance"] * 3, 2)


def test_storage_type_gp3_vs_io2():
    client = app.test_client()
    gp3 = client.post("/calculate", json=_payload(aws_storage_type="gp3")).get_json()
    io2 = client.post("/calculate", json=_payload(aws_storage_type="io2")).get_json()

    assert io2["aws"]["breakdown"]["storage"] > gp3["aws"]["breakdown"]["storage"]


def test_catalog_endpoint():
    client = app.test_client()
    res = client.get("/catalog")
    assert res.status_code == 200
    data = res.get_json()

    assert "aws" in data and "azure" in data and "gcp" in data and "storage_rates" in data
    assert len(data["aws"]) >= 20
    assert len(data["azure"]) >= 10
    assert len(data["gcp"]) >= 10


def test_smart_matcher_fallback():
    client = app.test_client()
    res = client.post("/calculate", json=_payload())
    assert res.status_code == 200
    data = res.get_json()

    assert data["aws"]["selected_instance"].get("sku")
