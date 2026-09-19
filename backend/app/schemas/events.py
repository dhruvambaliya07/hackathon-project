from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class EventSummary(BaseModel):
    id: UUID
    group_id: UUID | None = None
    title: str
    description: str
    starts_at: datetime
    location: str


class EventListQuery(BaseModel):
    group_id: UUID | None = None
    from_date: datetime | None = None
    page: int = 1
    page_size: int = 20