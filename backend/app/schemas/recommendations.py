from uuid import UUID

from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    user_id: UUID | None = None
    interest_text: str = Field(min_length=3, max_length=2000)
    limit: int = Field(default=10, ge=1, le=50)


class RecommendationItem(BaseModel):
    id: UUID
    type: str
    title: str
    description: str
    score: float = Field(ge=0, le=1)
    explanation: str


class RecommendationResult(BaseModel):
    recommendations: list[RecommendationItem] = Field(default_factory=list)