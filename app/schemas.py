import datetime
from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str


class TaskOut(BaseModel):
    id: int
    title: str
    is_complete: bool
    created_at: datetime.datetime
    completed_at: datetime.datetime | None = None

    class Config:
        from_attributes = True
