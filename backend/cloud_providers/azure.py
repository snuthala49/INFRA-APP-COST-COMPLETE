from .catalog_pricing import calculate_provider_cost


def azure_cost(
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
    azure_sku=None,
    pricing_model="on_demand",
    instance_count=1,
    azure_storage_type="standard_ssd",
    **_,
):
    if network is not None and not network_egress_gb_month:
        network_egress_gb_month = float(network) * 324
    return calculate_provider_cost(
        provider="azure",
        cpu=cpu,
        ram=ram,
        storage=storage,
        network_ingress_gb_month=network_ingress_gb_month,
        network_egress_gb_month=network_egress_gb_month,
        network_cross_region_gb_month=network_cross_region_gb_month,
        network_source_region=network_source_region,
        network_destination_region=network_destination_region,
        backup=backup,
        sku=azure_sku,
        pricing_model=pricing_model,
        instance_count=instance_count,
        storage_type=azure_storage_type,
    )
