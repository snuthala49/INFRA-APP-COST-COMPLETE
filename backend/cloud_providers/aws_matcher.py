"""
AWS Instance Matcher - Finds the best matching EC2 instance based on user requirements
"""
import json
import os
from typing import Dict, List, Optional


class AWSInstanceMatcher:
    """Matches user CPU/RAM requirements to the nearest AWS EC2 instance type."""
    
    def __init__(self, catalog_path: Optional[str] = None):
        if catalog_path is None:
            # Default to catalog in same directory
            catalog_path = os.path.join(
                os.path.dirname(__file__), 
                "aws_instance_catalog.json"
            )
        
        with open(catalog_path, 'r') as f:
            self.catalog = json.load(f)
        
        self.instances = self.catalog['instances']
        self.storage_pricing = self.catalog['storage_pricing']
        self.network_pricing = self.catalog['network_pricing']
        self.backup_pricing = self.catalog['backup_pricing']
    
    def find_best_instance(self, cpu: int, ram: float, prefer_memory: bool = False) -> Dict:
        """
        Find the best matching instance based on CPU and RAM requirements.
        
        Strategy:
        1. Filter instances that meet BOTH CPU and RAM requirements
        2. If none match, find the smallest instance that's bigger
        3. Prefer memory-optimized if RAM:CPU ratio is high
        
        Args:
            cpu: Number of vCPUs required
            ram: RAM in GB required
            prefer_memory: If True, prefer memory-optimized instances
        
        Returns:
            Dict with instance details
        """
        # Calculate RAM to CPU ratio to determine workload type
        ram_to_cpu_ratio = ram / cpu if cpu > 0 else 0
        
        # Filter instances that meet requirements
        matching = [
            inst for inst in self.instances
            if inst['vcpu'] >= cpu and inst['memory_gb'] >= ram
        ]
        
        if not matching:
            # No exact match, find smallest instance larger than requirements
            matching = [
                inst for inst in self.instances
                if inst['vcpu'] >= cpu or inst['memory_gb'] >= ram
            ]
        
        if not matching:
            # Fallback to largest instance
            matching = self.instances
        
        # Decide which instance to pick based on workload characteristics
        if ram_to_cpu_ratio > 6:  # Memory-heavy workload (>6 GB per vCPU)
            # Prefer r5 (memory-optimized) instances
            memory_optimized = [i for i in matching if i['category'] == 'memory']
            if memory_optimized:
                matching = memory_optimized
        elif ram_to_cpu_ratio < 3:  # CPU-heavy workload (<3 GB per vCPU)
            # Prefer c5 (compute-optimized) instances
            compute_optimized = [i for i in matching if i['category'] == 'compute']
            if compute_optimized:
                matching = compute_optimized
        
        # Sort by total cost and pick the cheapest that meets requirements
        matching.sort(key=lambda x: x['price_per_month'])
        
        return matching[0]
    
    def calculate_costs(
        self, 
        cpu: int, 
        ram: float, 
        storage: float, 
        network: float, 
        backup: float
    ) -> Dict:
        """
        Calculate total AWS costs including instance, storage, network, and backup.
        
        Args:
            cpu: vCPUs required
            ram: RAM in GB
            storage: Storage in GB
            network: Network bandwidth in Mbps (converted to GB transfer estimate)
            backup: Backup storage in GB
        
        Returns:
            Dict with cost breakdown and selected instance details
        """
        # Find best matching instance
        selected_instance = self.find_best_instance(cpu, ram)
        
        # Instance cost (compute)
        instance_cost = selected_instance['price_per_month']
        
        # Storage cost (EBS gp3)
        storage_cost = storage * self.storage_pricing['ebs_gp3']['price_per_gb_month']
        
        # Network cost (estimate: Mbps → monthly GB transfer)
        # Rough estimate: 1 Mbps sustained = ~324 GB/month (1 Mbps * 3600s * 24h * 30d / 8 bits)
        monthly_gb_transfer = network * 324  # Convert Mbps to GB/month
        network_cost = monthly_gb_transfer * self.network_pricing['data_transfer_out']['first_10tb_per_gb']
        
        # Backup cost (S3)
        backup_cost = backup * self.backup_pricing['s3_standard']['price_per_gb_month']
        
        # Total
        total = instance_cost + storage_cost + network_cost + backup_cost
        
        return {
            "provider": "aws",
            "total": round(total, 2),
            "currency": "USD",
            "selected_instance": {
                "type": selected_instance['instance_type'],
                "vcpu": selected_instance['vcpu'],
                "memory_gb": selected_instance['memory_gb'],
                "category": selected_instance['category'],
                "description": selected_instance['description'],
                "price_per_month": selected_instance['price_per_month']
            },
            "breakdown": {
                "compute": round(instance_cost, 2),
                "storage": round(storage_cost, 2),
                "network": round(network_cost, 2),
                "backup": round(backup_cost, 2)
            }
        }


# Create a singleton instance for easy import
_matcher = None

def get_matcher() -> AWSInstanceMatcher:
    """Get or create the AWS instance matcher singleton."""
    global _matcher
    if _matcher is None:
        _matcher = AWSInstanceMatcher()
    return _matcher
