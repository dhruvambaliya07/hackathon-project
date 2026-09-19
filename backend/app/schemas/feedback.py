from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FeedbackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    user_id: UUID
    recommendation_id: UUID
    feedback_type: Literal["interested", "not_interested", "already_joined", "wrong_match"]


class FeedbackResult(BaseModel):
    accepted: bool = True
    feedback_type: Literal["interested", "not_interested", "already_joined", "wrong_match"]