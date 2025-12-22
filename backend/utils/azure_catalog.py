import json
import os


def load_azure_catalog():
    """Load Azure instance SKUs from JSON catalog."""
    catalog_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "azure_catalog.json"
    )
    try:
        with open(catalog_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Azure catalog not found at {catalog_path}")


def find_best_fit(cpu, ram):
    """Find the best Azure instance SKU that fits the requested CPU and RAM.

    Strategy:
    1. Load Azure catalog.
    2. Filter SKUs where vcpu >= cpu and ram_gb >= ram (smallest first).
    3. If found, return the best-fit SKU with count=1.
    4. If not found, select the largest SKU and calculate count=ceil(cpu/largest.vcpu).

    Args:
        cpu: requested vCPU count
        ram: requested RAM in GB

    Returns:
        dict with sku, family, vcpu, ram_gb, price_per_hour, and count.
    """
    import math

    catalog = load_azure_catalog()

    # Sort by vcpu then by ram for consistent best-fit selection
    sorted_skus = sorted(catalog, key=lambda s: (s["vcpu"], s["ram_gb"]))

    # Find exact fit (vcpu >= cpu AND ram_gb >= ram)
    for sku in sorted_skus:
        if sku["vcpu"] >= cpu and sku["ram_gb"] >= ram:
            return {
                "sku": sku["sku"],
                "family": sku["family"],
                "vcpu": sku["vcpu"],
                "ram_gb": sku["ram_gb"],
                "price_per_hour": sku["price_per_hour"],
                "count": 1,
            }

    # No exact fit; use largest SKU and scale by vCPU
    largest = sorted_skus[-1]
    count = math.ceil(cpu / largest["vcpu"]) if largest["vcpu"] > 0 else 1
    return {
        "sku": largest["sku"],
        "family": largest["family"],
        "vcpu": largest["vcpu"],
        "ram_gb": largest["ram_gb"],
        "price_per_hour": largest["price_per_hour"],
        "count": count,
    }


def price_month_from_hour(hourly_price, instance_count=1):
    """Convert hourly price to monthly cost.

    Args:
        hourly_price: hourly rate in USD
        instance_count: number of instances

    Returns:
        monthly cost in USD (assuming 730 hours/month: 365 days * 24 / 12)
    """
    hours_per_month = 730
    return hourly_price * hours_per_month * instance_count
