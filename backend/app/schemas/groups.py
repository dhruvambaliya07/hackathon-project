from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class GroupSummary(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    name: str
    description: str
    category: str
    image_url: str | None = None
    location: str | None = None
    meeting_frequency: str | None = None
    member_count: int = Field(default=0, ge=0)


class GroupInterestResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    name: str
    category: str
    weight: float = Field(ge=0, le=1)


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


class GroupDetail(GroupSummary):
    interests: list[GroupInterestResponse] = Field(default_factory=list)
    upcoming_events: list[EventSummary] = Field(default_factory=list)


class GroupListQuery(BaseModel):
    category: str | None = None
    search: str | None = None
    interest: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)