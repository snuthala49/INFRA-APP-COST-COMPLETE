def calculate_onprem_tco(
    cpu=0,
    ram=0,
    storage=0,
    network=0,   # Mbps
    backup=0,    # GB
    instance_count=1,
):
    """
    Executive-level On-Prem TCO model (finance-grade).

    Assumptions:
    - 5-year amortization
    - 1.4x redundancy (HA + buffer)
    - $0.12/kWh power cost
    - PUE 1.56
    - Includes facilities + operations
    """

    try:
        count = max(int(instance_count), 1)
    except (TypeError, ValueError):
        count = 1

    # ---- Core assumptions ----
    amort_years = 5
    redundancy = 1.4
    power_rate = 0.12  # $/kWh
    pue = 1.56

    # ---- CapEx unit costs (Gartner-aligned enterprise blended) ----
    capex_per_vcpu = 500.0
    capex_per_gb_ram = 25.0
    capex_per_gb_storage = 0.15

    # ---- Power model (blended per compute unit) ----
    watts_per_vcpu = 5.0
    watts_per_gb_ram = 0.3
    watts_per_gb_storage = 0.05

    # ---- CapEx total ----
    capex_total = (
        cpu * capex_per_vcpu
        + ram * capex_per_gb_ram
        + storage * capex_per_gb_storage
    )

    # Amortized monthly with redundancy
    capex_monthly = (capex_total / (amort_years * 12)) * redundancy

    # ---- Power + cooling ----
    watts_total = (
        cpu * watts_per_vcpu
        + ram * watts_per_gb_ram
        + storage * watts_per_gb_storage
    )

    monthly_kwh = (watts_total / 1000.0) * 24 * 30 * pue
    power_cost = monthly_kwh * power_rate * redundancy

    # ---- Facilities (15% of CapEx monthly) ----
    facilities_cost = 0.15 * capex_monthly

    # ---- Operations (35% annually of CapEx → monthly) ----
    ops_cost = (0.35 * capex_total / 12)

    # ---- Hardware maintenance / support (12% annually of CapEx → monthly) ----
    maintenance_cost = 0.12 * capex_total / 12

    # ---- Software licensing: OS + hypervisor + monitoring ----
    software_licensing_cost = (cpu * 100.0) / 12

    # ---- Network ($0.02/GB egress — conservative middle ground) ----
    monthly_gb_transfer = network * 324  # Mbps → GB/month (Mbps × 3600×24×30 / 8 / 1024 / 1024 / 1024)
    network_cost = monthly_gb_transfer * 0.02

    # ---- Backup / DR ----
    backup_rate = 0.03  # $ per GB / month
    backup_cost = backup * backup_rate

    # ---- OpEx + Total (single workload baseline) ----
    opex_single = (
        power_cost
        + facilities_cost
        + ops_cost
        + maintenance_cost
        + software_licensing_cost
        + network_cost
        + backup_cost
    )
    capex_monthly *= count
    power_cost *= count
    facilities_cost *= count
    ops_cost *= count
    maintenance_cost *= count
    software_licensing_cost *= count
    network_cost *= count
    backup_cost *= count

    opex_monthly = opex_single * count
    total = capex_monthly + opex_monthly

    return {
        "provider": "onprem",
        "total": round(total, 2),
        "capex_monthly": round(capex_monthly, 2),
        "opex_monthly": round(opex_monthly, 2),
        "instance_count": count,
        "currency": "USD",
        "selected_instance": {
            "type": "On-prem workload baseline",
            "vcpu": cpu,
            "memory_gb": ram,
            "count": count,
            "category": "onprem",
            "description": "Modeled from requested workload inputs",
        },
        "assumptions": (
            "Per Garnter (Gartner-aligned) Executive TCO: 5yr amortization, 1.4x redundancy, $0.12/kWh, "
            "PUE 1.56, CapEx: $500/vCPU (hw+OS+support), $25/GB RAM, $0.15/GB storage, "
            "facilities 15%, ops 35% annually, maintenance 12% annually, software licensing $100/vCPU/year, "
            "network $0.02/GB egress (Mbps→GB/month), backup $0.03/GB"
        ),
        "breakdown": {
            "capex": round(capex_monthly, 2),
            "power": round(power_cost, 2),
            "facilities": round(facilities_cost, 2),
            "operations": round(ops_cost, 2),
            "maintenance": round(maintenance_cost, 2),
            "software_licensing": round(software_licensing_cost, 2),
            "network": round(network_cost, 2),
            "backup": round(backup_cost, 2),
        },
    }