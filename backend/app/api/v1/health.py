from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=ApiResponse[HealthResponse], summary="Check API and database health")
def health_check(db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> ApiResponse[HealthResponse]:
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unavailable"
    status = "ok" if db_status == "ok" else "degraded"
    return ApiResponse(data=HealthResponse(status=status, database=db_status, version=settings.app_version))