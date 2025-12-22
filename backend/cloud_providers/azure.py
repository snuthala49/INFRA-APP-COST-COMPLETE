
from utils.azure_catalog import find_best_fit, price_month_from_hour


def azure_cost(cpu=0, ram=0, storage=0, network=0, backup=0, **_):
    """Azure pricing model with instance selector.

    This implementation chooses a best-fit instance SKU from the Azure catalog and
    computes pricing using the SKU's hourly price (monthlyized). Storage/network/backup
    are charged with realistic per-unit rates.
    """
    # Azure realistic rates (per month per unit)
    storage_rate = 0.12  # $ per GB / month (managed disk)
    network_rate = 0.02  # $ per GB / month (data transfer)
    backup_rate = 0.05   # $ per GB / month (backup snapshots)

    # choose instance SKU and count
    selected = find_best_fit(cpu, ram)
    sku_hourly = float(selected.get('price_per_hour', 0.0))
    count = int(selected.get('count', 1))

    instance_month = price_month_from_hour(sku_hourly, count)

    storage_cost = storage * storage_rate
    network_cost = network * network_rate
    backup_cost = backup * backup_rate

    total = instance_month + storage_cost + network_cost + backup_cost

    return {
        "provider": "azure",
        "total": round(total, 2),
        "currency": "USD",
        "selected_instance": {
            "sku": selected.get('sku'),
            "family": selected.get('family'),
            "vcpu": selected.get('vcpu'),
            "ram_gb": selected.get('ram_gb'),
            "count": count,
            "price_per_hour": sku_hourly,
            "price_per_month": round(instance_month, 4),
        },
        "breakdown": {
            "instance": round(instance_month, 2),
            "storage": round(storage_cost, 2),
            "network": round(network_cost, 2),
            "backup": round(backup_cost, 2),
        },
    }
