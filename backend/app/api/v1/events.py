from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import ApiResponse, Meta
from app.schemas.events import EventDetail, EventListQuery, EventSummary
from app.services.catalog_service import get_event, list_events as query_events

router = APIRouter()


@router.get("", response_model=ApiResponse[list[EventSummary]], summary="List hobby events")
def list_events(
    group_id: UUID | None = None,
    search: str | None = None,
    category: str | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_db),
) -> ApiResponse[list[EventSummary]]:
    query = EventListQuery(group_id=group_id, search=search, category=category, from_date=from_date, to_date=to_date, page=page, page_size=page_size)
    items, total = query_events(
        session,
        search=query.search,
        group_id=query.group_id,
        category=query.category,
        from_date=query.from_date,
        to_date=query.to_date,
        page=query.page,
        page_size=query.page_size,
    )
    return ApiResponse(data=items, meta=Meta(page=query.page, page_size=query.page_size, total=total))


@router.get("/{event_id}", response_model=ApiResponse[EventDetail], summary="Get a hobby event")
def get_event_detail(event_id: UUID, session: Session = Depends(get_db)) -> ApiResponse[EventDetail]:
    event = get_event(session, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return ApiResponse(data=event)