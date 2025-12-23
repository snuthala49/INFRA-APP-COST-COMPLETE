from .azure_matcher import get_matcher

def azure_cost(cpu=0, ram=0, storage=0, network=0, backup=0, **_):
    """Azure pricing using real VM instance types and pricing.
    
    Uses Azure instance matcher to select appropriate VM size based on 
    CPU and RAM requirements, then calculates realistic costs.
    """
    matcher = get_matcher()
    return matcher.calculate_costs(cpu, ram, storage, network, backup)
