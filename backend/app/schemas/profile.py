from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ProfileUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    bio: str | None = Field(default=None, max_length=2000)
    interests: list[str] | None = Field(default=None, max_length=50)
    goals: list[str] | None = Field(default=None, max_length=20)

    @field_validator("interests", "goals")
    @classmethod
    def bound_item_lengths(cls, values: list[str] | None) -> list[str] | None:
        if values is not None and any(len(value) > 80 for value in values):
            raise ValueError("profile values are too long")
        return values


class ProfileUser(BaseModel):
    id: UUID
    name: str
    bio: str | None = None
    created_at: datetime
    updated_at: datetime


class ProfileInterest(BaseModel):
    id: UUID
    name: str
    category: str
    weight: float = Field(ge=0, le=1)


class ProfileGroup(BaseModel):
    id: UUID
    name: str
    description: str
    category: str
    location: str | None = None
    member_count: int = Field(ge=0)


class ProfileEvent(BaseModel):
    id: UUID
    group_id: UUID
    title: str
    description: str
    starts_at: datetime
    ends_at: datetime | None = None
    location: str


class ProfileResponse(BaseModel):
    user: ProfileUser
    interests: list[ProfileInterest] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    traits: list[str] = Field(default_factory=list)
    saved_groups: list[ProfileGroup] = Field(default_factory=list)
    interested_events: list[ProfileEvent] = Field(default_factory=list)