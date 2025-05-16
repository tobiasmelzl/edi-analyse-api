from pydantic import BaseModel


class StatusCodeOut(BaseModel):
    code: int
    description: str

    class Config:
        from_attributes = True
