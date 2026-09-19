from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import api_router
from app.config import get_settings
from app.schemas.common import ApiError, ApiResponse

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="REST API for discovering Aatmoday hobby communities and events.",
    docs_url="/docs",
    redoc_url="/redoc",
)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    payload = ApiResponse[None](error=ApiError(code="validation_error", message="Request validation failed.", details={"fields": exc.errors()}))
    return JSONResponse(status_code=422, content=payload.model_dump(mode="json"))


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    payload = ApiResponse[None](error=ApiError(code="http_error", message="The request could not be completed."))
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump(mode="json"))


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    payload = ApiResponse[None](error=ApiError(code="internal_error", message="An unexpected error occurred."))
    return JSONResponse(status_code=500, content=payload.model_dump(mode="json"))


app.include_router(api_router, prefix="/api/v1")