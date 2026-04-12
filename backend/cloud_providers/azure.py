from .catalog_pricing import calculate_provider_cost


def azure_cost(
    cpu=0,
    ram=0,
    storage=0,
    network=0,
    backup=0,
    azure_sku=None,
    pricing_model="on_demand",
    instance_count=1,
    azure_storage_type="standard_ssd",
    **_,
):
    return calculate_provider_cost(
        provider="azure",
        cpu=cpu,
        ram=ram,
        storage=storage,
        network=network,
        backup=backup,
        sku=azure_sku,
        pricing_model=pricing_model,
        instance_count=instance_count,
        storage_type=azure_storage_type,
    )
