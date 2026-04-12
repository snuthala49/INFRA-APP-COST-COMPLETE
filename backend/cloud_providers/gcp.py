from .catalog_pricing import calculate_provider_cost


def gcp_cost(
    cpu=0,
    ram=0,
    storage=0,
    network=0,
    backup=0,
    gcp_sku=None,
    pricing_model="on_demand",
    instance_count=1,
    gcp_storage_type="balanced_pd",
    **_,
):
    return calculate_provider_cost(
        provider="gcp",
        cpu=cpu,
        ram=ram,
        storage=storage,
        network=network,
        backup=backup,
        sku=gcp_sku,
        pricing_model=pricing_model,
        instance_count=instance_count,
        storage_type=gcp_storage_type,
    )
