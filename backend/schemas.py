from typing import Optional

from pydantic import BaseModel, Field, conint, confloat, model_validator


class CalcPayload(BaseModel):
    # CPU and RAM are per instance; storage, traffic, and backup are scenario totals.
    cpu: conint(ge=0)
    ram: confloat(ge=0, allow_inf_nan=False)
    storage: confloat(ge=0, allow_inf_nan=False)
    network_ingress_gb_month: confloat(ge=0, allow_inf_nan=False) = 0
    network_egress_gb_month: confloat(ge=0, allow_inf_nan=False) = 0
    backup: confloat(ge=0, allow_inf_nan=False)
    instance_count: int = Field(default=1, ge=1, le=500)
    pricing_model: str = Field(default="on_demand", pattern="^(on_demand|reserved_1yr|reserved_3yr|spot)$")
    aws_sku: Optional[str] = None
    azure_sku: Optional[str] = None
    gcp_sku: Optional[str] = None
    aws_storage_type: str = Field(default="gp3")
    azure_storage_type: str = Field(default="standard_ssd")
    gcp_storage_type: str = Field(default="balanced_pd")

    @model_validator(mode="before")
    @classmethod
    def convert_legacy_network_mbps(cls, value):
        if not isinstance(value, dict):
            return value

        normalized = dict(value)
        legacy_network_mbps = normalized.pop("network", None)
        if "network_egress_gb_month" not in normalized and legacy_network_mbps is not None:
            normalized["network_egress_gb_month"] = float(legacy_network_mbps) * 324
        return normalized


__all__ = ["CalcPayload"]
