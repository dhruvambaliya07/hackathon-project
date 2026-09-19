from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Query

from app.schemas.common import ApiResponse, Meta
from app.schemas.events import EventListQuery, EventSummary

router = APIRouter()


@router.get("", response_model=ApiResponse[list[EventSummary]], summary="List hobby events")
def list_events(group_id: UUID | None = None, from_date: datetime | None = None, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)) -> ApiResponse[list[EventSummary]]:
    EventListQuery(group_id=group_id, from_date=from_date, page=page, page_size=page_size)
    return ApiResponse(data=[], meta=Meta(page=page, page_size=page_size, total=0))


@router.get("/{event_id}", response_model=ApiResponse[EventSummary], summary="Get a hobby event")
def get_event(event_id: UUID) -> ApiResponse[EventSummary]:
    return ApiResponse(data=None, error={"code": "not_implemented", "message": f"Event {event_id} is not available in the foundation release."})