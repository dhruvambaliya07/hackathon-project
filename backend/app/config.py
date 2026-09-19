from functools import lru_cache
from typing import Literal

from pydantic import Field
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
    embedding_dimension: Literal[1536] = Field(1536, validation_alias="EMBEDDING_DIMENSION")
    cors_origins: str = Field(..., validation_alias="CORS_ORIGINS")
    sql_echo: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()