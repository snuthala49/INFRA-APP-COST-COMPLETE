"""
Azure Instance Matcher
Finds the best Azure VM instance based on CPU and RAM requirements.
"""
import json
import os

class AzureInstanceMatcher:
    def __init__(self, catalog_path=None):
        if catalog_path is None:
            catalog_path = os.path.join(os.path.dirname(__file__), 'azure_instance_catalog.json')
        
        with open(catalog_path, 'r') as f:
            self.catalog = json.load(f)
        
        self.instances = self.catalog['instances']
        self.storage_pricing = self.catalog['storage_pricing']
        self.network_pricing = self.catalog['network_pricing']
        self.backup_pricing = self.catalog['backup_pricing']
    
    def find_best_instance(self, cpu, ram):
        """
        Find the best matching Azure VM instance.
        
        Strategy:
        1. Calculate workload characteristics (RAM:CPU ratio)
        2. Filter instances that meet minimum requirements
        3. Prefer instances matching workload type
        4. Return cheapest option
        """
        # Calculate workload characteristics
        ram_to_cpu_ratio = ram / cpu if cpu > 0 else 0
        
        # Determine workload type
        if ram_to_cpu_ratio > 6:
            # Memory-intensive workload
            preferred_categories = ['memory', 'general', 'compute', 'burstable']
        elif ram_to_cpu_ratio < 3:
            # Compute-intensive workload
            preferred_categories = ['compute', 'general', 'burstable', 'memory']
        else:
            # Balanced workload
            preferred_categories = ['general', 'burstable', 'compute', 'memory']
        
        # Filter instances that meet requirements
        matching_instances = [
            inst for inst in self.instances
            if inst['vcpu'] >= cpu and inst['memory_gb'] >= ram
        ]
        
        if not matching_instances:
            # Fall back to largest instance
            return max(self.instances, key=lambda x: (x['vcpu'], x['memory_gb']))
        
        # Sort by category preference, then by price
        for preferred_category in preferred_categories:
            category_matches = [
                inst for inst in matching_instances
                if inst['category'] == preferred_category
            ]
            if category_matches:
                return min(category_matches, key=lambda x: x['price_per_month'])
        
        # Fallback: cheapest matching instance
        return min(matching_instances, key=lambda x: x['price_per_month'])
    
    def calculate_costs(self, cpu, ram, storage, network_mbps, backup_gb):
        """
        Calculate total Azure costs.
        
        Args:
            cpu: Number of vCPUs required
            ram: RAM in GB required
            storage: Storage in GB required
            network_mbps: Network bandwidth in Mbps
            backup_gb: Backup storage in GB
        
        Returns:
            dict with total, breakdown, and selected_instance
        """
        # Find best instance
        instance = self.find_best_instance(cpu, ram)
        
        # Calculate compute cost
        compute_cost = instance['price_per_month']
        
        # Calculate storage cost (using Standard SSD)
        storage_cost = storage * self.storage_pricing['standard_ssd_per_gb_month']
        
        # Calculate network cost
        # Estimate monthly data transfer: Mbps * 3600 * 24 * 30 / 8 / 1024
        monthly_gb = network_mbps * 3600 * 24 * 30 / 8 / 1024
        network_cost = monthly_gb * self.network_pricing['outbound_per_gb']
        
        # Calculate backup cost (using LRS)
        backup_cost = backup_gb * self.backup_pricing['lrs_per_gb_month']
        
        # Total
        total = compute_cost + storage_cost + network_cost + backup_cost
        
        return {
            "provider": "azure",
            "total": round(total, 2),
            "currency": "USD",
            "selected_instance": {
                "type": instance['instance_type'],
                "vcpu": instance['vcpu'],
                "memory_gb": instance['memory_gb'],
                "category": instance['category'],
                "description": instance['description'],
                "price_per_month": instance['price_per_month']
            },
            "breakdown": {
                "compute": round(compute_cost, 2),
                "storage": round(storage_cost, 2),
                "network": round(network_cost, 2),
                "backup": round(backup_cost, 2)
            }
        }

# Singleton instance
_matcher = None

def get_matcher():
    global _matcher
    if _matcher is None:
        _matcher = AzureInstanceMatcher()
    return _matcher
