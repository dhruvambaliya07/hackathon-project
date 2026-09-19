from uuid import UUID

from pydantic import BaseModel, Field


class FeedbackRequest(BaseModel):
    user_id: UUID
    target_type: str = Field(pattern="^(group|event|recommendation)$")
    target_id: UUID
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=2000)


class FeedbackResult(BaseModel):
    accepted: bool = True