"""
AWS cost calculation using real instance catalog and nearest-match algorithm.
"""
from .aws_matcher import get_matcher


def aws_cost(cpu=0, ram=0, storage=0, network=0, backup=0, **_):
    """
    Calculate AWS costs using real instance types and pricing.
    
    Automatically selects the best-matching EC2 instance based on CPU/RAM requirements,
    then adds costs for storage (EBS), network (data transfer), and backup (S3).
    
    Args:
        cpu: Number of vCPUs required
        ram: RAM in GB required
        storage: Storage in GB required
        network: Network bandwidth in Mbps
        backup: Backup storage in GB
    
    Returns:
        Dict with provider info, total cost, selected instance details, and breakdown
    """
    matcher = get_matcher()
    return matcher.calculate_costs(cpu, ram, storage, network, backup)
