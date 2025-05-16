from datetime import datetime
from typing import List
from pydantic import BaseModel


class KPIEntry(BaseModel):
    category: str
    count: int


class KPI(BaseModel):
    data: List[KPIEntry]
    period_start: datetime
    period_end: datetime
