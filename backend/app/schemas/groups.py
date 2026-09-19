from uuid import UUID

from pydantic import BaseModel, Field


class GroupSummary(BaseModel):
    id: UUID
    name: str
    description: str
    category: str


class GroupDetail(GroupSummary):
    member_count: int = Field(default=0, ge=0)
    upcoming_event_count: int = Field(default=0, ge=0)


class GroupListQuery(BaseModel):
    category: str | None = None
    search: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)