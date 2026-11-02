"""Database quote calculations based on cached provider price API records."""
from decimal import Decimal
import json
from typing import Dict, List, Optional

from utils.database_price_sync import DATABASE_SERVICES


def get_database_rate_catalog(
    cache: Dict,
    provider: str,
    service: str,
    region: str,
    component: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 250,
) -> Dict:
    if provider not in DATABASE_SERVICES:
        raise ValueError(f"Unsupported database provider: {provider}")
    if service not in DATABASE_SERVICES[provider]:
        raise ValueError(f"Unsupported {provider} database service: {service}")

    region_records = [
        record for record in cache.get("records", [])
        if record.get("provider") == provider
        and record.get("service") == service
        and (record.get("region") or "").lower() == region.lower()
    ]
    filtered_records = region_records
    if component and component != "all":
        filtered_records = [record for record in filtered_records if record.get("component") == component]
    if search:
        query = search.casefold()
        filtered_records = [
            record for record in filtered_records
            if query in " ".join((record.get("sku", ""), record.get("component", ""), record.get("unit", ""), json.dumps(record.get("dimensions", {}), sort_keys=True))).casefold()
        ]
    limit = min(max(int(limit), 1), 500)
    return {
        "provider": provider,
        "service": service,
        "region": region,
        "updated_at": cache.get("updated_at"),
        "provider_status": cache.get("providers", {}).get(provider, {"status": "unknown"}),
        "rates": filtered_records[:limit],
        "rate_count": len(filtered_records),
        "region_rate_count": len(region_records),
        "truncated": len(filtered_records) > limit,
    }


def calculate_database_quote(payload: Dict, cache: Dict) -> Dict:
    get_database_rate_catalog(cache, payload["provider"], payload["service"], payload["region"], limit=1)
    matching_rates = [
        rate for rate in cache.get("records", [])
        if rate.get("provider") == payload["provider"]
        and rate.get("service") == payload["service"]
        and (rate.get("region") or "").lower() == payload["region"].lower()
    ]
    if not matching_rates:
        raise ValueError(
            f"No cached {payload['provider']} {payload['service']} prices for region {payload['region']}; sync the database price catalog first"
        )

    rates_by_id = {rate["rate_id"]: rate for rate in matching_rates}
    line_items: List[Dict] = []
    currencies = set()
    total = Decimal("0")

    for requested in payload["line_items"]:
        rate = rates_by_id.get(requested["rate_id"])
        if rate is None:
            raise ValueError("A selected database price rate is not available in the requested provider, service, and region")
        quantity = Decimal(str(requested["quantity"]))
        unit_price = Decimal(str(rate["unit_price"]))
        line_total = quantity * unit_price
        currencies.add(rate.get("currency", "USD"))
        total += line_total
        line_items.append({
            "rate_id": rate["rate_id"],
            "component": rate["component"],
            "sku": rate["sku"],
            "quantity": float(quantity),
            "unit": rate.get("unit"),
            "unit_price": float(unit_price),
            "subtotal": round(float(line_total), 6),
            "source": rate.get("source"),
            "effective_date": rate.get("effective_date"),
        })

    if len(currencies) != 1:
        raise ValueError("All selected database rates must use the same currency")

    return {
        "provider": payload["provider"],
        "service": payload["service"],
        "region": payload["region"],
        "currency": currencies.pop(),
        "total": round(float(total), 2),
        "line_items": line_items,
        "price_status": cache.get("providers", {}).get(payload["provider"], {"status": "unknown"}),
        "prices_updated_at": cache.get("updated_at"),
        "assumption": "Each quantity is billed in the exact unit shown for its selected provider price record.",
    }