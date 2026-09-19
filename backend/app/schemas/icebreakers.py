from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StrictStr


class IcebreakerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    user_id: UUID
    target_type: Literal["group", "event"]
    target_id: UUID
    style: Literal["casual", "friendly", "professional"] = "casual"


class AIIcebreakerResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    icebreaker: StrictStr = Field(min_length=1, max_length=280)


class IcebreakerResult(BaseModel):
    icebreaker: str = Field(min_length=1)
    style: Literal["casual", "friendly", "professional"]