from typing import Optional

from pydantic import BaseModel, Field, conint, confloat


class CalcPayload(BaseModel):
    cpu: conint(ge=0)
    ram: confloat(ge=0)
    storage: confloat(ge=0)
    network: confloat(ge=0)
    backup: confloat(ge=0)
    instance_count: int = Field(default=1, ge=1, le=500)
    pricing_model: str = Field(default="on_demand", pattern="^(on_demand|reserved_1yr|reserved_3yr|spot)$")
    aws_sku: Optional[str] = None
    azure_sku: Optional[str] = None
    gcp_sku: Optional[str] = None
    aws_storage_type: str = Field(default="gp3")
    azure_storage_type: str = Field(default="standard_ssd")
    gcp_storage_type: str = Field(default="balanced_pd")


__all__ = ["CalcPayload"]
