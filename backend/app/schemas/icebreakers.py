from uuid import UUID

from pydantic import BaseModel, Field


class IcebreakerRequest(BaseModel):
    user_id: UUID | None = None
    group_id: UUID | None = None
    event_id: UUID | None = None
    context: str | None = Field(default=None, max_length=1000)


class IcebreakerResult(BaseModel):
    prompts: list[str] = Field(default_factory=list)
    status: str = "pending"