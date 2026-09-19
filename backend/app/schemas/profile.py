from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProfileUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=120)
    bio: str | None = Field(default=None, max_length=2000)


class ProfileResponse(BaseModel):
    id: UUID
    display_name: str
    bio: str | None = None
    created_at: datetime
    updated_at: datetime