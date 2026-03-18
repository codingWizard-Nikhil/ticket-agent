from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TicketCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assignee: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: str = "medium"


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: Optional[str] = None
    status: Optional[str] = None


class TicketResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    assignee: Optional[str]
    deadline: Optional[datetime]
    priority: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
