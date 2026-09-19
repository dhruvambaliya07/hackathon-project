from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class IcebreakerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    user_id: UUID
    target_type: Literal["group", "event"]
    target_id: UUID
    style: Literal["casual", "friendly", "professional"] = "casual"


class IcebreakerResult(BaseModel):
    icebreaker: str = Field(min_length=1)
    style: Literal["casual", "friendly", "professional"]