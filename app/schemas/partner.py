from datetime import datetime
from pydantic import BaseModel

class PartnerBase(BaseModel):
    name: str
    identifier: str

class PartnerCreate(PartnerBase):
    pass

class PartnerOut(PartnerBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True
