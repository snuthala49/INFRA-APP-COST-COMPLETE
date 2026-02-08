def k8s_cost(cpu=0, ram=0, storage=0, network=0, backup=0, **_):
    """Neutral on-prem Kubernetes baseline model.

    Assumptions:
    - Utilization target 60–70% (model uses 65%)
    - Real-world utilization 40–50% (model uses 45%)
    - 3-year amortization, 1.5x redundancy, $0.12/kWh, PUE 1.5
    """
    # Utilization assumptions
    target_util = 0.65
    real_util = 0.45

    # Scale required capacity based on real utilization
    effective_cpu = cpu / real_util if real_util > 0 else cpu
    effective_ram = ram / real_util if real_util > 0 else ram
    effective_storage = storage / real_util if real_util > 0 else storage

    # Baseline infra costs (same assumptions as on-prem)
    amort_years = 3
    redundancy = 1.5
    power_rate = 0.12
    pue = 1.5

    capex_per_vcpu = 400.0
    capex_per_gb_ram = 30.0
    capex_per_gb_storage = 0.08

    watts_per_vcpu = 10.0
    watts_per_gb_ram = 0.5
    watts_per_gb_storage = 0.1

    capex_total = (effective_cpu * capex_per_vcpu) + (effective_ram * capex_per_gb_ram) + (effective_storage * capex_per_gb_storage)
    capex_monthly = (capex_total / (amort_years * 12)) * redundancy

    watts_total = (effective_cpu * watts_per_vcpu) + (effective_ram * watts_per_gb_ram) + (effective_storage * watts_per_gb_storage)
    monthly_kwh = (watts_total / 1000.0) * 24 * 30 * pue
    power_cost = monthly_kwh * power_rate * redundancy

    # Kubernetes operational overhead (control plane, ops, tooling)
    k8s_overhead = 0.15 * (capex_monthly + power_cost)

    # Network and backup costs (neutral baseline)
    network_rate = 0.04  # $ per Mbps / month
    backup_rate = 0.02   # $ per GB / month

    network_cost = network * network_rate
    backup_cost = backup * backup_rate

    total = capex_monthly + power_cost + k8s_overhead + network_cost + backup_cost

    return {
        "provider": "kubernetes",
        "total": round(total, 2),
        "currency": "USD",
        "assumptions": "K8s neutral on-prem baseline: 60–70% target util (65%), 40–50% real util (45%), 3-year amort, 1.5x redundancy, $0.12/kWh, network $0.04/Mbps, backup $0.02/GB",
        "breakdown": {
            "cpu": round(capex_monthly, 2),
            "ram": round(power_cost, 2),
            "storage": round(k8s_overhead, 2),
            "network": round(network_cost, 2),
            "backup": round(backup_cost, 2),
        },
    }
