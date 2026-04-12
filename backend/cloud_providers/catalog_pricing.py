import json
import os
from typing import Dict, List, Optional


HOURS_PER_MONTH = 730

NETWORK_PRICING_PER_GB = {
    "aws": 0.09,
    "azure": 0.087,
    "gcp": 0.12,
}

BACKUP_PRICING_PER_GB = {
    "aws": 0.023,
    "azure": 0.02,
    "gcp": 0.02,
}

DEFAULT_STORAGE_TYPE = {
    "aws": "gp3",
    "azure": "standard_ssd",
    "gcp": "balanced_pd",
}


def _data_path(file_name: str) -> str:
    return os.path.join(os.path.dirname(__file__), "..", "data", file_name)


def load_catalog(provider: str) -> List[Dict]:
    with open(_data_path(f"{provider}_catalog.json"), "r") as f:
        return json.load(f)


def load_storage_rates() -> Dict[str, Dict[str, float]]:
    with open(_data_path("storage_rates.json"), "r") as f:
        return json.load(f)


def hourly_on_demand(entry: Dict) -> float:
    rate = entry.get("price_per_hour", 0)
    if isinstance(rate, dict):
        return float(rate.get("on_demand", 0))
    return float(rate or 0)


def hourly_by_model(entry: Dict, pricing_model: str) -> float:
    rate = entry.get("price_per_hour", 0)
    if isinstance(rate, dict):
        return float(rate.get(pricing_model) or rate.get("on_demand") or 0)
    return float(rate or 0)


def lookup_sku(catalog: List[Dict], sku: Optional[str]) -> Optional[Dict]:
    if not sku:
        return None
    for entry in catalog:
        if entry.get("sku") == sku:
            return entry
    return None


def smart_match(catalog: List[Dict], cpu: float, ram: float) -> Dict:
    target_cpu = max(float(cpu), 0.0)
    target_ram = max(float(ram), 0.0)
    ratio = (target_ram / target_cpu) if target_cpu > 0 else 0

    candidates = [entry for entry in catalog if entry.get("vcpu", 0) >= target_cpu and entry.get("ram_gb", 0) >= target_ram]
    if not candidates:
        candidates = list(catalog)

    if ratio > 6:
        preferred = [entry for entry in candidates if entry.get("category") == "memory"]
        if preferred:
            candidates = preferred
    elif ratio < 3 and target_cpu > 0:
        preferred = [entry for entry in candidates if entry.get("category") == "compute"]
        if preferred:
            candidates = preferred

    candidates.sort(key=lambda entry: (hourly_on_demand(entry), entry.get("vcpu", 0), entry.get("ram_gb", 0)))
    return candidates[0]


def calculate_provider_cost(
    provider: str,
    cpu: float,
    ram: float,
    storage: float,
    network: float,
    backup: float,
    sku: Optional[str],
    pricing_model: str,
    instance_count: int,
    storage_type: Optional[str],
) -> Dict:
    catalog = load_catalog(provider)
    storage_rates = load_storage_rates().get(provider, {})

    selected = lookup_sku(catalog, sku) or smart_match(catalog, cpu, ram)

    selected_storage_type = storage_type if storage_type in storage_rates else DEFAULT_STORAGE_TYPE[provider]
    storage_rate = float(storage_rates.get(selected_storage_type, 0.10))

    hourly = hourly_by_model(selected, pricing_model)
    per_instance_monthly = hourly * HOURS_PER_MONTH
    compute_cost = per_instance_monthly * instance_count

    storage_cost = max(float(storage), 0.0) * storage_rate

    monthly_gb_transfer = max(float(network), 0.0) * 324
    network_cost = monthly_gb_transfer * NETWORK_PRICING_PER_GB[provider]

    backup_cost = max(float(backup), 0.0) * BACKUP_PRICING_PER_GB[provider]

    total = compute_cost + storage_cost + network_cost + backup_cost

    return {
        "provider": provider,
        "total": round(total, 2),
        "currency": "USD",
        "pricing_model": pricing_model,
        "instance_count": int(instance_count),
        "storage_type": selected_storage_type,
        "selected_instance": {
            "sku": selected.get("sku"),
            "type": selected.get("sku"),
            "vcpu": selected.get("vcpu"),
            "memory_gb": selected.get("ram_gb"),
            "category": selected.get("category"),
            "description": selected.get("description"),
            "price_per_hour": round(hourly, 5),
            "price_per_month": round(per_instance_monthly, 2),
            "count": int(instance_count),
        },
        "breakdown": {
            "instance": round(compute_cost, 2),
            "storage": round(storage_cost, 2),
            "network": round(network_cost, 2),
            "backup": round(backup_cost, 2),
        },
    }