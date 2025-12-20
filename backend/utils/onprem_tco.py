def calculate_onprem_tco(cpu=0, ram=0, storage=0, network=0, backup=0, **kwargs):
	"""Simple on-prem TCO placeholder returning a structured response.

	This is still illustrative, but returns the same schema as cloud providers so the frontend
	can rely on a consistent structure.
	"""
	# Example internal cost assumptions
	cpu_rate = 8.0
	ram_rate = 3.0
	storage_rate = 0.015

	cpu_cost = cpu * cpu_rate
	ram_cost = ram * ram_rate
	storage_cost = storage * storage_rate

	total = cpu_cost + ram_cost + storage_cost

	return {
		"provider": "onprem",
		"total": round(total, 2),
		"currency": "USD",
		"breakdown": {
			"cpu": round(cpu_cost, 2),
			"ram": round(ram_cost, 2),
			"storage": round(storage_cost, 2),
		},
	}
