from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class TransactionBase(BaseModel):
    reference_number: str
    message_type: str
    direction: str
    status: int
    partner_id: int
    storage_path: Optional[str] = None
    error_message: Optional[str] = None

class TransactionOut(TransactionBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True
