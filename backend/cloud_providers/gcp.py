from .catalog_pricing import calculate_provider_cost


def gcp_cost(
    cpu=0,
    ram=0,
    storage=0,
    network_ingress_gb_month=0,
    network_egress_gb_month=0,
    network_cross_region_gb_month=0,
    network_source_region=None,
    network_destination_region=None,
    network=None,
    backup=0,
    gcp_sku=None,
    pricing_model="on_demand",
    instance_count=1,
    gcp_storage_type="balanced_pd",
    **_,
):
    if network is not None and not network_egress_gb_month:
        network_egress_gb_month = float(network) * 324
    return calculate_provider_cost(
        provider="gcp",
        cpu=cpu,
        ram=ram,
        storage=storage,
        network_ingress_gb_month=network_ingress_gb_month,
        network_egress_gb_month=network_egress_gb_month,
        network_cross_region_gb_month=network_cross_region_gb_month,
        network_source_region=network_source_region,
        network_destination_region=network_destination_region,
        backup=backup,
        sku=gcp_sku,
        pricing_model=pricing_model,
        instance_count=instance_count,
        storage_type=gcp_storage_type,
    )
