from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Meta(BaseModel):
    request_id: str | None = None
    page: int | None = Field(default=None, ge=1)
    page_size: int | None = Field(default=None, ge=1, le=100)
    total: int | None = Field(default=None, ge=0)


class ApiResponse(BaseModel, Generic[T]):
    data: T | None = None
    meta: Meta = Field(default_factory=Meta)
    error: "ApiError | None" = None


class ApiError(BaseModel):
    code: str
    message: str
    details: dict[str, Any] | None = None