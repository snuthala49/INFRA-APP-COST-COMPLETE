"""Fetch and normalize public cloud database price catalogs.

Prices are cached locally so calculator requests do not depend on provider API
latency. Azure and AWS sources are public; GCP Cloud Billing requires an API key.
"""
import argparse
import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import requests

LOGGER = logging.getLogger(__name__)
BASE_DIR = Path(__file__).parent.parent
DEFAULT_CACHE_PATH = BASE_DIR / "cache" / "database_prices.json"
AWS_OFFER_URL = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/{service}/current/{region}/index.json"
AZURE_RETAIL_URL = "https://prices.azure.com/api/retail/prices"
GCP_SERVICES_URL = "https://cloudbilling.googleapis.com/v1/services"
GCP_SERVICE_NAMES = {
    "cloud_sql": ("Cloud SQL",),
    "spanner": ("Cloud Spanner",),
    "firestore": ("Firestore",),
    "bigtable": ("Bigtable",),
    "bigquery": ("BigQuery",),
}
AZURE_DATABASE_SERVICES = {
    "SQL Database": "azure_sql",
    "SQL Managed Instance": "azure_sql_managed_instance",
    "Azure Cosmos DB": "cosmos_db",
    "Azure Database for PostgreSQL": "azure_postgresql",
    "SQL Data Warehouse": "synapse",
}
AWS_DATABASE_SERVICES = {
    "AmazonRDS": "rds",
    "AmazonDynamoDB": "dynamodb",
    "AmazonRedshift": "redshift",
}
AWS_REGION_LOCATIONS = {
    "us-east-1": "US East (N. Virginia)",
    "us-east-2": "US East (Ohio)",
    "us-west-1": "US West (N. California)",
    "us-west-2": "US West (Oregon)",
    "eu-west-1": "EU (Ireland)",
}
DATABASE_SERVICES = {
    "aws": ("rds", "aurora", "dynamodb", "redshift"),
    "azure": ("azure_sql", "azure_sql_managed_instance", "cosmos_db", "azure_postgresql", "synapse"),
    "gcp": ("cloud_sql", "spanner", "firestore", "bigtable", "bigquery"),
}


def _component(label: str) -> str:
    value = label.lower()
    if any(token in value for token in ("instance", "node", "compute", "cpu", "vcpu", "acu")):
        return "compute"
    if any(token in value for token in ("storage", "gb-month", "giby.mo", "data stored")):
        return "storage"
    if any(token in value for token in ("backup", "snapshot")):
        return "backup"
    if any(token in value for token in ("iops", "provisioned io")):
        return "iops"
    if any(token in value for token in ("read request", "read request unit", "read unit")):
        return "read"
    if any(token in value for token in ("write request", "write request unit", "write unit")):
        return "write"
    if any(token in value for token in ("request", "operation", "query", "read", "write")):
        return "operations"
    return "other"


def _rate_record(
    provider: str,
    service: str,
    sku: str,
    component: str,
    region: Optional[str],
    unit: Optional[str],
    price: float,
    currency: str,
    source: str,
    effective_date: Optional[str],
    dimensions: Optional[Dict] = None,
    pricing_model: str = "on_demand",
) -> Dict:
    rate = {
        "provider": provider,
        "service": service,
        "sku": sku,
        "component": component,
        "region": region,
        "unit": unit,
        "unit_price": round(float(price), 12),
        "currency": currency,
        "source": source,
        "effective_date": effective_date,
        "pricing_model": pricing_model,
        "dimensions": dimensions or {},
    }
    rate_identity = json.dumps(rate, sort_keys=True, separators=(",", ":"), default=str)
    rate["rate_id"] = hashlib.sha256(rate_identity.encode("utf-8")).hexdigest()[:20]
    return rate


def parse_aws_offer(data: Dict, service_code: str, region: str) -> List[Dict]:
    """Normalize matching AWS On-Demand offer dimensions for one region."""
    service = AWS_DATABASE_SERVICES[service_code]
    publication_date = data.get("publicationDate")
    source = AWS_OFFER_URL.format(service=service_code, region=region)
    records = []
    products = data.get("products", {})
    terms_by_sku = data.get("terms", {}).get("OnDemand", {})

    for product_id, product in products.items():
        attributes = product.get("attributes", {})
        product_service = service
        if service_code == "AmazonRDS" and "aurora" in attributes.get("databaseEngine", "").lower():
            product_service = "aurora"
        product_region = attributes.get("regionCode")
        if product_region and product_region != region:
            continue
        expected_location = AWS_REGION_LOCATIONS.get(region, region)
        if not product_region and attributes.get("location") not in (None, expected_location):
            continue

        product_family = product.get("productFamily", "")
        product_name = product.get("product", {}).get("attributes", {}).get("instanceType", "")
        sku = attributes.get("instanceType") or attributes.get("volumeType") or product_id
        for term in terms_by_sku.get(product_id, {}).values():
            for dimension in term.get("priceDimensions", {}).values():
                price = dimension.get("pricePerUnit", {}).get("USD")
                if price is None:
                    continue
                try:
                    numeric_price = float(price)
                except (TypeError, ValueError):
                    continue
                label = " ".join((product_family, dimension.get("description", ""), product_name))
                records.append(_rate_record(
                    provider="aws",
                    service=product_service,
                    sku=sku,
                    component=_component(label),
                    region=region,
                    unit=dimension.get("unit"),
                    price=numeric_price,
                    currency="USD",
                    source=source,
                    effective_date=publication_date,
                    dimensions=attributes,
                ))
    return records


def parse_azure_retail(data: Dict, service_filter: Dict[str, str], region: str) -> List[Dict]:
    """Normalize Azure Retail Price API items for supported database services."""
    records = []
    for item in data.get("Items", []):
        service_name = item.get("serviceName")
        service = service_filter.get(service_name)
        if not service or item.get("armRegionName", "").lower() != region.lower():
            continue
        if item.get("priceType", "Consumption") not in ("Consumption", "Reservation"):
            continue
        price = item.get("unitPrice", item.get("retailPrice"))
        if price is None:
            continue
        records.append(_rate_record(
            provider="azure",
            service=service,
            sku=item.get("armSkuName") or item.get("skuName") or item.get("productName", "unknown"),
            component=_component(" ".join((item.get("productName", ""), item.get("skuName", ""), item.get("armSkuName", ""), item.get("meterName", ""), item.get("unitOfMeasure", "")))),
            region=item.get("armRegionName"),
            unit=item.get("unitOfMeasure"),
            price=price,
            currency=item.get("currencyCode", "USD"),
            source=AZURE_RETAIL_URL,
            effective_date=item.get("effectiveStartDate"),
            dimensions={
                "service_name": service_name,
                "product_name": item.get("productName"),
                "sku_name": item.get("skuName"),
                "meter_name": item.get("meterName"),
                "reservation_term": item.get("reservationTerm"),
            },
            pricing_model="reserved" if item.get("priceType") == "Reservation" else "on_demand",
        ))
    return records


def _gcp_unit_price(value: Dict) -> float:
    return float(value.get("units", 0)) + float(value.get("nanos", 0)) / 1_000_000_000


def parse_gcp_skus(data: Dict, service: str, region: str) -> List[Dict]:
    """Normalize Google Cloud Billing SKUs, retaining the first tiered rate."""
    records = []
    for sku in data.get("skus", []):
        regions = sku.get("serviceRegions", [])
        if regions and region not in regions:
            continue
        for price_info in sku.get("pricingInfo", []):
            expression = price_info.get("pricingExpression", {})
            tiers = expression.get("tieredRates", [])
            if not tiers:
                continue
            unit_price = tiers[0].get("unitPrice", {})
            currency = unit_price.get("currencyCode", "USD")
            records.append(_rate_record(
                provider="gcp",
                service=service,
                sku=sku.get("skuId", sku.get("description", "unknown")),
                component=_component(" ".join((sku.get("description", ""), expression.get("usageUnitDescription", "")))),
                region=region,
                unit=expression.get("usageUnitDescription") or expression.get("usageUnit"),
                price=_gcp_unit_price(unit_price),
                currency=currency,
                source="https://cloudbilling.googleapis.com/v1/services",
                effective_date=price_info.get("effectiveTime"),
                dimensions={
                    "description": sku.get("description"),
                    "service_regions": regions,
                    "tiered_rates": [
                        {"start_usage_amount": tier.get("startUsageAmount", 0), "unit_price": _gcp_unit_price(tier.get("unitPrice", {}))}
                        for tier in tiers
                    ],
                },
            ))
    return records


def fetch_aws_database_prices(region: str, session=requests) -> List[Dict]:
    records = []
    for service_code in AWS_DATABASE_SERVICES:
        url = AWS_OFFER_URL.format(service=service_code, region=region)
        response = session.get(url, timeout=90)
        response.raise_for_status()
        records.extend(parse_aws_offer(response.json(), service_code, region))
    return records


def fetch_azure_database_prices(region: str, session=requests) -> List[Dict]:
    region_filter = region.replace("'", "''")
    service_names = " or ".join(
        f"serviceName eq '{name}'" for name in AZURE_DATABASE_SERVICES
    )
    filter_value = f"armRegionName eq '{region_filter}' and ({service_names})"
    url = AZURE_RETAIL_URL
    params = {"api-version": "2023-01-01-preview", "$filter": filter_value, "currencyCode": "USD"}
    records = []
    while url:
        response = session.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        records.extend(parse_azure_retail(data, AZURE_DATABASE_SERVICES, region))
        url = data.get("NextPageLink")
        params = None
    return records


def fetch_gcp_database_prices(region: str, api_key: Optional[str] = None, session=requests) -> List[Dict]:
    api_key = api_key or os.getenv("GOOGLE_CLOUD_BILLING_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_CLOUD_BILLING_API_KEY is required to fetch GCP database prices")

    service_ids = {}
    page_token = None
    while True:
        params = {"pageSize": 5000}
        if page_token:
            params["pageToken"] = page_token
        response = session.get(GCP_SERVICES_URL, params=params, headers={"x-goog-api-key": api_key}, timeout=30)
        response.raise_for_status()
        data = response.json()
        for item in data.get("services", []):
            display_name = item.get("displayName", "")
            for service, aliases in GCP_SERVICE_NAMES.items():
                if any(alias.lower() in display_name.lower() for alias in aliases):
                    service_ids[service] = item.get("name", "").rsplit("/", 1)[-1]
        page_token = data.get("nextPageToken")
        if not page_token:
            break

    records = []
    for service, service_id in service_ids.items():
        if not service_id:
            continue
        page_token = None
        while True:
            params = {"pageSize": 5000}
            if page_token:
                params["pageToken"] = page_token
            response = session.get(
                f"{GCP_SERVICES_URL}/{service_id}/skus",
                params=params,
                headers={"x-goog-api-key": api_key},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            records.extend(parse_gcp_skus(data, service, region))
            page_token = data.get("nextPageToken")
            if not page_token:
                break
    return records


def sync_database_prices(
    aws_region: str = "us-east-1",
    azure_region: str = "eastus",
    gcp_region: str = "us-central1",
    cache_path: Path = DEFAULT_CACHE_PATH,
    session=requests,
) -> Dict:
    """Refresh providers independently and retain prior data when one is unavailable."""
    cache_path = Path(cache_path)
    previous = load_database_price_cache(cache_path)
    cached_by_provider = {
        provider: [record for record in previous.get("records", []) if record.get("provider") == provider]
        for provider in ("aws", "azure", "gcp")
    }
    provider_status = previous.get("providers", {})
    now = datetime.now(timezone.utc).isoformat()
    fetchers = (
        ("aws", lambda: fetch_aws_database_prices(aws_region, session=session), aws_region),
        ("azure", lambda: fetch_azure_database_prices(azure_region, session=session), azure_region),
        ("gcp", lambda: fetch_gcp_database_prices(gcp_region, session=session), gcp_region),
    )

    for provider, fetch_prices, region in fetchers:
        try:
            fresh_records = fetch_prices()
            if not fresh_records:
                raise RuntimeError("No database price records matched the selected region")
            cached_by_provider[provider] = fresh_records
            provider_status[provider] = {
                "status": "current",
                "region": region,
                "record_count": len(fresh_records),
                "updated_at": now,
            }
        except Exception as error:
            old_status = provider_status.get(provider, {})
            provider_status[provider] = {
                "status": "stale" if cached_by_provider[provider] else "unavailable",
                "region": old_status.get("region", region),
                "record_count": len(cached_by_provider[provider]),
                "updated_at": old_status.get("updated_at"),
                "error": str(error),
            }

    records = [record for provider_records in cached_by_provider.values() for record in provider_records]

    payload = {
        "updated_at": now,
        "providers": provider_status,
        "records": records,
    }
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = cache_path.with_suffix(cache_path.suffix + ".tmp")
    temporary_path.write_text(json.dumps(payload, indent=2))
    temporary_path.replace(cache_path)
    return payload


def load_database_price_cache(cache_path: Path = DEFAULT_CACHE_PATH) -> Dict:
    cache_path = Path(cache_path)
    if not cache_path.exists():
        return {"updated_at": None, "providers": {}, "records": []}
    return json.loads(cache_path.read_text())


def main():
    parser = argparse.ArgumentParser(description="Sync database prices from cloud provider catalogs")
    parser.add_argument("--aws-region", default="us-east-1")
    parser.add_argument("--azure-region", default="eastus")
    parser.add_argument("--gcp-region", default="us-central1")
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE_PATH)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    result = sync_database_prices(args.aws_region, args.azure_region, args.gcp_region, args.cache)
    LOGGER.info("Cached %d database price records to %s", len(result["records"]), args.cache)


if __name__ == "__main__":
    main()