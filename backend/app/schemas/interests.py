from pydantic import BaseModel, Field


class InterestAnalyzeRequest(BaseModel):
    text: str = Field(min_length=3, max_length=2000, description="Natural-language description of the student's interests.")


class InterestAnalysis(BaseModel):
    original_text: str
    interests: list[str] = Field(default_factory=list)
    preferences: list[str] = Field(default_factory=list)
    status: str = "pending"