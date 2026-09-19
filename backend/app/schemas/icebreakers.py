from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class IcebreakerRequest(BaseModel):
    user_id: UUID
    target_type: Literal["group", "event"]
    target_id: UUID
    style: Literal["casual", "friendly", "professional"] = "casual"


class IcebreakerResult(BaseModel):
    icebreaker: str = Field(min_length=1)
    style: Literal["casual", "friendly", "professional"]