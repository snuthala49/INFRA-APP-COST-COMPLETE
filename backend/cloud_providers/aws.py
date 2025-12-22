
from utils.aws_catalog import find_best_fit, price_month_from_hour


def aws_cost(cpu=0, ram=0, storage=0, network=0, backup=0, **_):
    """AWS pricing model (MVP with instance selector).

    This implementation chooses a best-fit instance SKU from a compact catalog and
    computes pricing using the SKU's hourly price (monthlyized). Storage/network/backup
    are charged with simple per-unit rates (same as before) for MVP.
    """
    # AWS realistic rates (per month per unit)
    storage_rate = 0.10  # $ per GB / month (EBS gp3 standard)
    network_rate = 0.02  # $ per GB / month (NAT/data transfer average)
    backup_rate = 0.05   # $ per GB / month (EBS snapshots)

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
        "provider": "aws",
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
