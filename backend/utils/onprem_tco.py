def calculate_onprem_tco(
    cpu=0,
    ram=0,
    storage=0,
    network=0,   # Mbps
    backup=0,    # GB
):
    """
    Executive-level On-Prem TCO model (finance-grade).

    Assumptions:
    - 4-year amortization
    - 1.4x redundancy (HA + buffer)
    - $0.10/kWh power cost
    - PUE 1.5
    - Includes facilities + operations
    """

    # ---- Core assumptions ----
    amort_years = 4
    redundancy = 1.4
    power_rate = 0.10  # $/kWh
    pue = 1.5

    # ---- CapEx unit costs (realistic enterprise blended) ----
    capex_per_vcpu = 150.0
    capex_per_gb_ram = 10.0
    capex_per_gb_storage = 0.05

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

    # ---- Operations (25% annually of CapEx → monthly) ----
    ops_cost = (0.25 * capex_total / 12) * redundancy

    # ---- Network (normalized to cloud-style transfer model) ----
    # Convert sustained Mbps to estimated monthly GB transfer for apples-to-apples comparison
    monthly_gb_transfer = network * 3600 * 24 * 30 / 8 / 1024
    network_rate_per_gb = 0.03  # $ per GB / month (enterprise blended WAN/transit baseline)
    network_cost = monthly_gb_transfer * network_rate_per_gb

    # ---- Backup / DR ----
    backup_rate = 0.03  # $ per GB / month
    backup_cost = backup * backup_rate

    # ---- OpEx + Total ----
    opex_monthly = (
        power_cost
        + facilities_cost
        + ops_cost
        + network_cost
        + backup_cost
    )
    total = capex_monthly + opex_monthly

    return {
        "provider": "onprem",
        "total": round(total, 2),
        "capex_monthly": round(capex_monthly, 2),
        "opex_monthly": round(opex_monthly, 2),
        "currency": "USD",
        "assumptions": (
            "Executive TCO: 4yr amortization, 1.4x redundancy, $0.10/kWh, "
            "PUE 1.5, facilities 15%, ops 25% annually, "
            "network converted Mbps→GB at $0.03/GB, backup $0.03/GB"
        ),
        "breakdown": {
            "capex": round(capex_monthly, 2),
            "power": round(power_cost, 2),
            "facilities": round(facilities_cost, 2),
            "operations": round(ops_cost, 2),
            "network": round(network_cost, 2),
            "backup": round(backup_cost, 2),
        },
    }