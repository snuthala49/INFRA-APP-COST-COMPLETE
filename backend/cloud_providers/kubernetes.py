def k8s_cost(cpu=0, ram=0, storage=0, network=0, backup=0, instance_count=1, **_):
    """Neutral on-prem Kubernetes baseline model.

    Assumptions:
    - Utilization target 60–70% (model uses 65%)
    - Real-world utilization 40–50% (model uses 45%)
    - 5-year amortization, 1.5x redundancy, $0.12/kWh, PUE 1.56
    """
    # Utilization assumptions
    target_util = 0.65
    real_util = 0.45

    try:
        count = max(int(instance_count), 1)
    except (TypeError, ValueError):
        count = 1

    # Scale required capacity based on real utilization
    effective_cpu = cpu / real_util if real_util > 0 else cpu
    effective_ram = ram / real_util if real_util > 0 else ram
    effective_storage = storage / real_util if real_util > 0 else storage

    # Baseline infra costs (same assumptions as on-prem)
    amort_years = 5
    redundancy = 1.5
    power_rate = 0.12
    pue = 1.56

    capex_per_vcpu = 500.0
    capex_per_gb_ram = 25.0
    capex_per_gb_storage = 0.15

    watts_per_vcpu = 10.0
    watts_per_gb_ram = 0.5
    watts_per_gb_storage = 0.1

    capex_total = (effective_cpu * capex_per_vcpu) + (effective_ram * capex_per_gb_ram) + (effective_storage * capex_per_gb_storage)
    capex_monthly = (capex_total / (amort_years * 12)) * redundancy

    watts_total = (effective_cpu * watts_per_vcpu) + (effective_ram * watts_per_gb_ram) + (effective_storage * watts_per_gb_storage)
    monthly_kwh = (watts_total / 1000.0) * 24 * 30 * pue
    power_cost = monthly_kwh * power_rate * redundancy

    # Kubernetes operational overhead (control plane, tooling)
    k8s_overhead = 0.15 * (capex_monthly + power_cost)

    # Additional datacenter and IT operations lines for fair on-prem comparison
    facilities_cost = 0.15 * capex_monthly
    ops_cost = (0.25 * capex_total / 12)
    maintenance_cost = 0.12 * capex_total / 12
    software_licensing_cost = (cpu * 80.0) / 12

    # Network and backup costs (neutral baseline)
    backup_rate = 0.02   # $ per GB / month

    # Convert Mbps to monthly GB transfer (Mbps → Gbps → GB/month)
    # 3600s * 24h * 30d = 2,592,000 seconds/month
    # Mbps * 2,592,000 / 8 bits→bytes / 1024 KB / 1024 MB / 1024 GB = Mbps * 324 GB/month
    monthly_gb_transfer = network * 324
    network_cost = monthly_gb_transfer * 0.03
    backup_cost = backup * backup_rate

    breakdown = {
        "capex": round(capex_monthly, 2),
        "power": round(power_cost, 2),
        "facilities": round(facilities_cost, 2),
        "operations": round(ops_cost, 2),
        "maintenance": round(maintenance_cost, 2),
        "software_licensing": round(software_licensing_cost, 2),
        "k8s_overhead": round(k8s_overhead, 2),
        "network": round(network_cost, 2),
        "backup": round(backup_cost, 2),
    }
    if count > 1:
        breakdown = {k: round(v * count, 2) for k, v in breakdown.items()}

    total = round(sum(breakdown.values()), 2)

    return {
        "provider": "kubernetes",
        "total": total,
        "instance_count": count,
        "currency": "USD",
        "pricing_model": "onprem_k8s",
        "selected_instance": {
            "type": "K8s workload baseline",
            "vcpu": cpu,
            "memory_gb": ram,
            "count": count,
            "category": "cluster",
            "description": f"Requested workload: {cpu} vCPU / {ram} GB RAM. Provisioned baseline for 45% real utilization: {round(effective_cpu, 2)} vCPU / {round(effective_ram, 2)} GB RAM",
            "provisioned_vcpu": round(effective_cpu, 2),
            "provisioned_memory_gb": round(effective_ram, 2),
        },
        "assumptions": "Per Garnter (Gartner-aligned) K8s baseline: 60–70% target util (65%), 40–50% real util (45%), 5-year amort, 1.5x redundancy, $0.12/kWh, PUE 1.56, CapEx: $500/vCPU (hw+OS+support), $25/GB RAM, $0.15/GB storage (utilization-scaled), facilities 15% of capex monthly, ops 25% annualized capex monthly, maintenance 12% annually, software licensing $80/vCPU/year, +15% k8s overhead, network Mbps→GB at $0.03/GB, backup $0.02/GB",
        "breakdown": breakdown,
    }
