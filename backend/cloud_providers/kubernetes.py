def k8s_cost(cpu=0, ram=0, storage=0, network=0, backup=0, **_):
    """Simple Kubernetes cost estimator using same inputs as other providers.

    This is an illustrative, per-cluster estimate (uses the same resource inputs as other providers).
    """
    # Rates (example)
    cpu_rate = 11.0      # $ per vCPU / month (slightly higher to account for orchestration overhead)
    ram_rate = 4.5       # $ per GB / month
    storage_rate = 0.03  # $ per GB / month
    network_rate = 0.04  # $ per Mbps / month

    cpu_cost = cpu * cpu_rate
    ram_cost = ram * ram_rate
    storage_cost = storage * storage_rate
    network_cost = network * network_rate

    total = cpu_cost + ram_cost + storage_cost + network_cost

    return {
        "provider": "kubernetes",
        "total": round(total, 2),
        "currency": "USD",
        "breakdown": {
            "cpu": round(cpu_cost, 2),
            "ram": round(ram_cost, 2),
            "storage": round(storage_cost, 2),
            "network": round(network_cost, 2),
        },
    }
