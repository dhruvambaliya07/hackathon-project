from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.groups import GroupInterestResponse


class EventSummary(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    group_id: UUID
    title: str
    description: str
    starts_at: datetime
    ends_at: datetime | None = None
    location: str
    capacity: int | None = Field(default=None, ge=0)
    image_url: str | None = None


class EventGroupResponse(BaseModel):
    id: UUID
    name: str
    category: str


class EventDetail(EventSummary):
    group: EventGroupResponse
    interests: list[GroupInterestResponse] = Field(default_factory=list)
    related_events: list[EventSummary] = Field(default_factory=list)


class EventListQuery(BaseModel):
    group_id: UUID | None = None
    category: str | None = None
    search: str | None = None
    from_date: datetime | None = None
    to_date: datetime | None = None
    page: int = 1
    page_size: int = 20