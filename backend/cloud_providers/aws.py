from .catalog_pricing import calculate_provider_cost


def aws_cost(
    cpu=0,
    ram=0,
    storage=0,
    network_ingress_gb_month=0,
    network_egress_gb_month=0,
    network=None,
    backup=0,
    aws_sku=None,
    pricing_model="on_demand",
    instance_count=1,
    aws_storage_type="gp3",
    **_,
):
    if network is not None and not network_egress_gb_month:
        network_egress_gb_month = float(network) * 324
    return calculate_provider_cost(
        provider="aws",
        cpu=cpu,
        ram=ram,
        storage=storage,
        network_ingress_gb_month=network_ingress_gb_month,
        network_egress_gb_month=network_egress_gb_month,
        backup=backup,
        sku=aws_sku,
        pricing_model=pricing_model,
        instance_count=instance_count,
        storage_type=aws_storage_type,
    )
