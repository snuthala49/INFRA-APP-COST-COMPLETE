
def aws_cost(cpu=0, ram=0, storage=0, network=0, backup=0, **_):
    """Simple AWS pricing model (illustrative only).

    Returns a structured dict with total (rounded to 2 decimals), currency and a breakdown.
    """
    cpu_rate = 10.0      # $ per vCPU / month
    ram_rate = 4.0       # $ per GB / month
    storage_rate = 0.02  # $ per GB / month
    network_rate = 0.05  # $ per Mbps / month
    backup_rate = 0.01   # $ per GB / month

    cpu_cost = cpu * cpu_rate
    ram_cost = ram * ram_rate
    storage_cost = storage * storage_rate
    network_cost = network * network_rate
    backup_cost = backup * backup_rate

    total = cpu_cost + ram_cost + storage_cost + network_cost + backup_cost

    return {
        "provider": "aws",
        "total": round(total, 2),
        "currency": "USD",
        "breakdown": {
            "cpu": round(cpu_cost, 2),
            "ram": round(ram_cost, 2),
            "storage": round(storage_cost, 2),
            "network": round(network_cost, 2),
            "backup": round(backup_cost, 2),
        },
    }
