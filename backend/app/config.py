from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Aatmoday Connect API"
    app_version: str = "0.1.0"
    environment: str = "development"
    database_url: str = Field(..., validation_alias="DATABASE_URL")
    ai_api_key: str = Field(..., validation_alias="AI_API_KEY")
    ai_model: str = Field(..., validation_alias="AI_MODEL")
    ai_api_url: str = Field("https://api.openai.com/v1/chat/completions", validation_alias="AI_API_URL")
    ai_timeout_seconds: float = Field(10.0, gt=0, le=60, validation_alias="AI_TIMEOUT_SECONDS")
    embedding_model: str = Field(..., validation_alias="EMBEDDING_MODEL")
    embedding_api_url: str = Field("https://api.openai.com/v1/embeddings", validation_alias="EMBEDDING_API_URL")
    embedding_timeout_seconds: float = Field(10.0, gt=0, le=60, validation_alias="EMBEDDING_TIMEOUT_SECONDS")
    embedding_dimension: Literal[1536] = Field(1536, validation_alias="EMBEDDING_DIMENSION")
    semantic_weight: float = Field(0.50, ge=0, le=1, validation_alias="SEMANTIC_WEIGHT")
    interest_overlap_weight: float = Field(0.25, ge=0, le=1, validation_alias="INTEREST_OVERLAP_WEIGHT")
    goal_compatibility_weight: float = Field(0.15, ge=0, le=1, validation_alias="GOAL_COMPATIBILITY_WEIGHT")
    event_relevance_weight: float = Field(0.10, ge=0, le=1, validation_alias="EVENT_RELEVANCE_WEIGHT")
    cors_origins: str = Field(..., validation_alias="CORS_ORIGINS")
    sql_echo: bool = False

    @field_validator("cors_origins")
    @classmethod
    def reject_wildcard_cors(cls, value: str) -> str:
        if "*" in {origin.strip() for origin in value.split(",")}: 
            raise ValueError("CORS_ORIGINS must list explicit origins")
        return value

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()