def k8s_cost(cpu=0, ram=0, storage=0, network_ingress_gb_month=0, network_egress_gb_month=0, network_cross_region_gb_month=0, network_source_region=None, network_destination_region=None, backup=0, instance_count=1, network=None, **_):
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
    total_cpu = cpu * count
    total_ram = ram * count
    effective_cpu = total_cpu / real_util if real_util > 0 else total_cpu
    effective_ram = total_ram / real_util if real_util > 0 else total_ram
    effective_storage = storage

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
    software_licensing_cost = (total_cpu * 80.0) / 12

    # Network and backup costs (neutral baseline)
    backup_rate = 0.02   # $ per GB / month

    if network is not None and not network_egress_gb_month:
        network_egress_gb_month = float(network) * 324
    network_cost = max(float(network_egress_gb_month), 0.0) * 0.03
    cross_region_cost = max(float(network_cross_region_gb_month), 0.0) * 0.03
    backup_cost = backup * backup_rate

    breakdown = {
        "capex": round(capex_monthly, 2),
        "power": round(power_cost, 2),
        "facilities": round(facilities_cost, 2),
        "operations": round(ops_cost, 2),
        "maintenance": round(maintenance_cost, 2),
        "software_licensing": round(software_licensing_cost, 2),
        "k8s_overhead": round(k8s_overhead, 2),
        "network_egress": round(network_cost, 2),
        "network_cross_region": round(cross_region_cost, 2),
        "network_ingress": 0.0,
        "backup": round(backup_cost, 2),
    }
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
            "description": f"Requested workload: {total_cpu} vCPU / {total_ram} GB RAM across {count} instances. Provisioned baseline for 45% real utilization: {round(effective_cpu, 2)} vCPU / {round(effective_ram, 2)} GB RAM",
            "provisioned_vcpu": round(effective_cpu, 2),
            "provisioned_memory_gb": round(effective_ram, 2),
        },
        "assumptions": "Kubernetes infrastructure baseline: 45% real utilization, 5-year amortization, 1.5x redundancy, $0.12/kWh, PUE 1.56, monthly egress and cross-region transfer at $0.03/GB, backup at $0.02/GB. Storage, network, and backup are scenario totals; CPU and RAM are per instance.",
        "breakdown": breakdown,
        "price_provenance": {"source": "Static infrastructure assumptions", "region": None, "region_status": "not applicable to this generic baseline", "last_updated": None},
        "network_transfer": {
            "source_region": network_source_region,
            "destination_region": network_destination_region,
            "cross_region_gb_month": round(float(network_cross_region_gb_month), 2),
        },
    }
