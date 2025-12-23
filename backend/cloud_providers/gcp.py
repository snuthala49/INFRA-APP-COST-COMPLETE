from .gcp_matcher import get_matcher

def gcp_cost(cpu=0, ram=0, storage=0, network=0, backup=0, **_):
    """GCP pricing using real Compute Engine instance types and pricing.
    
    Uses GCP instance matcher to select appropriate machine type based on 
    CPU and RAM requirements, then calculates realistic costs.
    """
    matcher = get_matcher()
    return matcher.calculate_costs(cpu, ram, storage, network, backup)
