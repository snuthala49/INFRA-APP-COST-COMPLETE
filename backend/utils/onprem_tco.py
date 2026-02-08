def calculate_onprem_tco(cpu=0, ram=0, storage=0, network=0, backup=0, **kwargs):
	"""On-prem TCO baseline model with industry-style assumptions.

	Assumptions:
	- 3-year amortization
	- 1.5x redundancy
	- $0.12/kWh power cost
	- PUE 1.5
	"""
	# Baseline assumptions
	amort_years = 3
	redundancy = 1.5
	power_rate = 0.12  # $/kWh
	pue = 1.5

	# CapEx unit costs (baseline industry-style placeholders)
	capex_per_vcpu = 400.0
	capex_per_gb_ram = 30.0
	capex_per_gb_storage = 0.08

	# Power draw estimates (watts)
	watts_per_vcpu = 10.0
	watts_per_gb_ram = 0.5
	watts_per_gb_storage = 0.1

	# CapEx amortized monthly
	capex_total = (cpu * capex_per_vcpu) + (ram * capex_per_gb_ram) + (storage * capex_per_gb_storage)
	capex_monthly = (capex_total / (amort_years * 12)) * redundancy

	# Power + cooling monthly
	watts_total = (cpu * watts_per_vcpu) + (ram * watts_per_gb_ram) + (storage * watts_per_gb_storage)
	monthly_kwh = (watts_total / 1000.0) * 24 * 30 * pue
	power_cost = monthly_kwh * power_rate * redundancy

	# Ops/maintenance overhead (10% of capex+power)
	overhead = 0.10 * (capex_monthly + power_cost)

	# Network and backup baseline costs (industry-style placeholders)
	network_rate = 0.02  # $ per Mbps / month
	backup_rate = 0.02   # $ per GB / month

	network_cost = network * network_rate
	backup_cost = backup * backup_rate

	total = capex_monthly + power_cost + overhead + network_cost + backup_cost

	return {
		"provider": "onprem",
		"total": round(total, 2),
		"currency": "USD",
		"assumptions": "On-prem baseline: 3-year amortization, 1.5x redundancy, $0.12/kWh, PUE 1.5, network $0.02/Mbps, backup $0.02/GB",
		"breakdown": {
			"cpu": round(capex_monthly, 2),
			"ram": round(power_cost, 2),
			"storage": round(overhead, 2),
			"network": round(network_cost, 2),
			"backup": round(backup_cost, 2),
		},
	}
