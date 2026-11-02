import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.database_price_sync import (
    AZURE_DATABASE_SERVICES,
    GCP_SERVICES_URL,
    fetch_azure_database_prices,
    fetch_gcp_database_prices,
    load_database_price_cache,
    parse_aws_offer,
    parse_azure_retail,
    parse_gcp_skus,
    sync_database_prices,
)
import app as app_module


def test_parse_aws_rds_on_demand_compute_price_by_region():
    offer = {
        "publicationDate": "2026-10-01T00:00:00Z",
        "products": {
            "sku1": {
                "productFamily": "Database Instance",
                "attributes": {
                    "databaseEngine": "PostgreSQL",
                    "instanceType": "db.t3.medium",
                    "deploymentOption": "Single-AZ",
                    "regionCode": "us-east-1",
                    "location": "US East (N. Virginia)",
                },
            },
            "sku2": {
                "productFamily": "Database Instance",
                "attributes": {"instanceType": "db.t3.medium", "regionCode": "us-west-2"},
            },
        },
        "terms": {
            "OnDemand": {
                "sku1": {
                    "term1": {
                        "priceDimensions": {
                            "dimension1": {"unit": "Hrs", "description": "db.t3.medium instance", "pricePerUnit": {"USD": "0.068"}}
                        }
                    }
                }
            }
        },
    }

    records = parse_aws_offer(offer, "AmazonRDS", "us-east-1")

    assert len(records) == 1
    assert records[0]["service"] == "rds"
    assert records[0]["sku"] == "db.t3.medium"
    assert records[0]["component"] == "compute"
    assert records[0]["unit_price"] == 0.068
    assert records[0]["region"] == "us-east-1"


def test_parse_aws_aurora_from_rds_offer():
    offer = {
        "products": {
            "aurora-sku": {
                "productFamily": "Database Instance",
                "attributes": {"databaseEngine": "Aurora PostgreSQL", "instanceType": "db.r6g.large", "regionCode": "us-east-1"},
            }
        },
        "terms": {"OnDemand": {"aurora-sku": {"term": {"priceDimensions": {"hour": {"unit": "Hrs", "pricePerUnit": {"USD": "0.25"}}}}}}},
    }
    records = parse_aws_offer(offer, "AmazonRDS", "us-east-1")
    assert records[0]["service"] == "aurora"


def test_parse_azure_database_retail_rate_with_effective_date():
    payload = {
        "Items": [
            {
                "serviceName": "Azure Database for PostgreSQL",
                "armRegionName": "eastus",
                "armSkuName": "Standard_D2s_v3",
                "meterName": "Compute - General Purpose",
                "unitOfMeasure": "1 Hour",
                "unitPrice": 0.22,
                "currencyCode": "USD",
                "priceType": "Consumption",
                "effectiveStartDate": "2026-09-01T00:00:00Z",
            },
            {
                "serviceName": "Azure Database for PostgreSQL",
                "armRegionName": "westus",
                "armSkuName": "Standard_D2s_v3",
                "meterName": "Compute - General Purpose",
                "unitOfMeasure": "1 Hour",
                "unitPrice": 0.24,
            },
        ]
    }

    records = parse_azure_retail(payload, {"Azure Database for PostgreSQL": "azure_postgresql"}, "eastus")

    assert len(records) == 1
    assert records[0]["service"] == "azure_postgresql"
    assert records[0]["component"] == "compute"
    assert records[0]["unit_price"] == 0.22
    assert records[0]["effective_date"] == "2026-09-01T00:00:00Z"


def test_azure_sql_database_public_service_name_maps_to_catalog_service():
    payload = {
        "Items": [
            {
                "serviceName": "SQL Database",
                "armRegionName": "eastus",
                "armSkuName": "GP_Gen5_2",
                "productName": "SQL Database General Purpose - Compute Gen5",
                "meterName": "vCore",
                "unitOfMeasure": "1 Hour",
                "unitPrice": 0.25,
                "currencyCode": "USD",
                "priceType": "Consumption",
            },
            {
                "serviceName": "SQL Data Warehouse",
                "armRegionName": "eastus",
                "skuName": "DW100c",
                "productName": "SQL Data Warehouse Compute",
                "meterName": "Compute",
                "unitOfMeasure": "1 Hour",
                "unitPrice": 1.0,
                "currencyCode": "USD",
                "priceType": "Consumption",
            },
            {
                "serviceName": "SQL Managed Instance",
                "armRegionName": "eastus",
                "armSkuName": "GP_Gen5_2",
                "productName": "SQL Managed Instance General Purpose - Compute Gen5",
                "meterName": "vCore",
                "unitOfMeasure": "1 Hour",
                "unitPrice": 0.3,
                "currencyCode": "USD",
                "priceType": "Consumption",
            },
        ]
    }
    records = parse_azure_retail(payload, AZURE_DATABASE_SERVICES, "eastus")
    assert {record["service"] for record in records} == {"azure_sql", "azure_sql_managed_instance", "synapse"}
    azure_sql_compute = next(record for record in records if record["service"] == "azure_sql")
    assert azure_sql_compute["component"] == "compute"


def test_azure_fetch_follows_next_page():
    first_page = {"Items": [], "NextPageLink": "https://prices.azure.com/next"}
    second_page = {"Items": [], "NextPageLink": None}

    class Response:
        def __init__(self, payload):
            self.payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self.payload

    class Session:
        def __init__(self):
            self.calls = []

        def get(self, url, params=None, timeout=None):
            self.calls.append((url, params))
            return Response(first_page if len(self.calls) == 1 else second_page)

    session = Session()
    assert fetch_azure_database_prices("eastus", session=session) == []
    assert len(session.calls) == 2
    assert session.calls[1][0] == "https://prices.azure.com/next"


def test_parse_gcp_sku_base_tier_and_currency():
    payload = {
        "skus": [
            {
                "skuId": "CLOUDSQL-CPU",
                "description": "Cloud SQL CPU running in us-central1",
                "serviceRegions": ["us-central1"],
                "pricingInfo": [
                    {
                        "effectiveTime": "2026-10-01T00:00:00Z",
                        "pricingExpression": {
                            "usageUnit": "h",
                            "usageUnitDescription": "hour",
                            "tieredRates": [
                                {"startUsageAmount": 0, "unitPrice": {"currencyCode": "USD", "units": "0", "nanos": 310000000}}
                            ],
                        },
                    }
                ],
            },
            {"skuId": "OTHER-REGION", "description": "Other", "serviceRegions": ["europe-west1"]},
        ]
    }

    records = parse_gcp_skus(payload, "cloud_sql", "us-central1")

    assert len(records) == 1
    assert records[0]["service"] == "cloud_sql"
    assert records[0]["component"] == "compute"
    assert records[0]["unit_price"] == 0.31
    assert records[0]["dimensions"]["tiered_rates"][0]["unit_price"] == 0.31


def test_gcp_database_sync_requires_api_key(monkeypatch):
    monkeypatch.delenv("GOOGLE_CLOUD_BILLING_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="GOOGLE_CLOUD_BILLING_API_KEY"):
        fetch_gcp_database_prices("us-central1")


def test_gcp_database_sync_uses_api_key_header_and_service_skus():
    class Response:
        def __init__(self, payload):
            self.payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self.payload

    class Session:
        def __init__(self):
            self.calls = []

        def get(self, url, params=None, headers=None, timeout=None):
            self.calls.append((url, params or {}, headers or {}))
            if url == GCP_SERVICES_URL:
                return Response({"services": [{"name": "services/cloudsql", "displayName": "Cloud SQL"}]})
            if url.endswith("/services/cloudsql/skus"):
                return Response({
                    "skus": [{
                        "skuId": "CLOUDSQL-CPU",
                        "description": "Cloud SQL CPU",
                        "serviceRegions": ["us-central1"],
                        "pricingInfo": [{
                            "effectiveTime": "2026-10-01T00:00:00Z",
                            "pricingExpression": {
                                "usageUnit": "h",
                                "tieredRates": [{"unitPrice": {"currencyCode": "USD", "units": "0", "nanos": 310000000}}],
                            },
                        }],
                    }]
                })
            return Response({"skus": []})

    session = Session()
    records = fetch_gcp_database_prices("us-central1", api_key="test-api-key", session=session)

    assert len(records) == 1
    assert records[0]["service"] == "cloud_sql"
    assert records[0]["unit_price"] == 0.31
    assert all(call[2].get("x-goog-api-key") == "test-api-key" for call in session.calls)
    assert all("key" not in call[1] for call in session.calls)


def test_database_sync_caches_public_providers_when_gcp_is_unconfigured(monkeypatch, tmp_path):
    monkeypatch.setattr("utils.database_price_sync.fetch_aws_database_prices", lambda region, session: [{"provider": "aws", "region": region}])
    monkeypatch.setattr("utils.database_price_sync.fetch_azure_database_prices", lambda region, session: [{"provider": "azure", "region": region}])

    def missing_gcp_key(region, session):
        raise RuntimeError("GOOGLE_CLOUD_BILLING_API_KEY is required")

    monkeypatch.setattr("utils.database_price_sync.fetch_gcp_database_prices", missing_gcp_key)
    cache_path = tmp_path / "database_prices.json"
    result = sync_database_prices(cache_path=cache_path)

    assert {record["provider"] for record in result["records"]} == {"aws", "azure"}
    assert result["providers"]["aws"]["status"] == "current"
    assert result["providers"]["azure"]["status"] == "current"
    assert result["providers"]["gcp"]["status"] == "unavailable"
    assert load_database_price_cache(cache_path)["records"] == result["records"]


def test_database_catalog_route_returns_cached_records(monkeypatch):
    monkeypatch.setattr(app_module, "load_database_price_cache", lambda: {"updated_at": "now", "providers": {}, "records": [{"provider": "aws"}]})
    response = app_module.app.test_client().get("/api/database/catalog")
    assert response.status_code == 200
    assert response.get_json()["services"]["aws"] == ["rds", "aurora", "dynamodb", "redshift"]


def test_database_catalog_route_reports_no_cache(monkeypatch):
    monkeypatch.setattr(app_module, "load_database_price_cache", lambda: {"updated_at": None, "providers": {}, "records": []})
    response = app_module.app.test_client().get("/api/database/catalog")
    assert response.status_code == 503
    assert response.get_json()["error"] == "Database prices have not been synced"


def test_database_catalog_route_filters_by_provider_service_and_region(monkeypatch):
    records = [
        {"rate_id": "east", "provider": "aws", "service": "rds", "region": "us-east-1", "component": "compute", "sku": "db.t3.medium", "unit": "Hrs"},
        {"rate_id": "east-2", "provider": "aws", "service": "rds", "region": "us-east-1", "component": "compute", "sku": "db.m6g.large", "unit": "Hrs"},
        {"rate_id": "west", "provider": "aws", "service": "rds", "region": "us-west-2", "component": "compute", "sku": "db.t3.medium", "unit": "Hrs"},
        {"rate_id": "azure", "provider": "azure", "service": "azure_sql", "region": "eastus", "component": "storage", "sku": "Premium", "unit": "GB-Mo"},
    ]
    monkeypatch.setattr(app_module, "load_database_price_cache", lambda: {"updated_at": "now", "providers": {}, "records": records})
    response = app_module.app.test_client().get("/api/database/catalog?provider=aws&service=rds&region=us-east-1&component=compute&search=db.t3&limit=1")
    assert response.status_code == 200
    assert [rate["rate_id"] for rate in response.get_json()["rates"]] == ["east"]
    assert response.get_json()["rate_count"] == 1
    assert response.get_json()["region_rate_count"] == 2


def test_database_quote_uses_cached_api_unit_prices(monkeypatch):
    records = [
        {
            "rate_id": "compute-hourly",
            "provider": "aws",
            "service": "rds",
            "region": "us-east-1",
            "component": "compute",
            "sku": "db.t3.medium",
            "unit": "Hrs",
            "unit_price": 0.068,
            "currency": "USD",
            "source": "AWS Price List",
            "effective_date": "2026-10-01",
        },
        {
            "rate_id": "storage-monthly",
            "provider": "aws",
            "service": "rds",
            "region": "us-east-1",
            "component": "storage",
            "sku": "gp3",
            "unit": "GB-Mo",
            "unit_price": 0.12,
            "currency": "USD",
            "source": "AWS Price List",
            "effective_date": "2026-10-01",
        },
    ]
    monkeypatch.setattr(app_module, "load_database_price_cache", lambda: {"updated_at": "now", "providers": {"aws": {"status": "current"}}, "records": records})
    response = app_module.app.test_client().post("/api/database/calculate", json={
        "provider": "aws",
        "service": "rds",
        "region": "us-east-1",
        "line_items": [
            {"rate_id": "compute-hourly", "quantity": 730},
            {"rate_id": "storage-monthly", "quantity": 100},
        ],
    })

    assert response.status_code == 200
    result = response.get_json()
    assert result["total"] == 61.64
    assert result["currency"] == "USD"
    assert [line["subtotal"] for line in result["line_items"]] == [49.64, 12.0]


def test_database_quote_rejects_rate_from_another_region(monkeypatch):
    monkeypatch.setattr(app_module, "load_database_price_cache", lambda: {"records": []})
    response = app_module.app.test_client().post("/api/database/calculate", json={
        "provider": "aws",
        "service": "rds",
        "region": "us-east-1",
        "line_items": [{"rate_id": "missing", "quantity": 730}],
    })
    assert response.status_code == 422
    assert "No cached" in response.get_json()["error"]