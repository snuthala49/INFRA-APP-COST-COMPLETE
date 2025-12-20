from pydantic import BaseModel, conint, confloat


class CalcPayload(BaseModel):
    cpu: conint(ge=0)
    ram: confloat(ge=0)
    storage: confloat(ge=0)
    network: confloat(ge=0)
    backup: confloat(ge=0)


__all__ = ["CalcPayload"]
