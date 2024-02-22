from typing import Optional
from pydantic import BaseModel, validator
from datetime import datetime

class VoucherPayload(BaseModel):
    id: int
    code: str
    max_redemptions: int
    expiry_date: datetime | None

    #function ensures max_redemptions var is positive 
    @validator("max_redemptions")
    def check_max_redemptions(cls, v):
        if v <= 0:
            raise ValueError("max_redemptions must be positive")
        return v
