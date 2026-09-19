from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class InterestAnalyzeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(min_length=3, max_length=2000, description="Natural-language description of the student's interests.")

    @field_validator("text")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("text must not be blank")
        return normalized


class AnalyzedInterest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    confidence: float = Field(ge=0, le=1)


class InterestAnalysis(BaseModel):
    original_text: str
    interests: list[AnalyzedInterest] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    traits: list[str] = Field(default_factory=list)
    source: Literal["ai", "fallback"] = "ai"
