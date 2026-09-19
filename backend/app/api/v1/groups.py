from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.groups import GroupDetail, GroupListQuery, GroupSummary
from app.services.catalog_service import get_group, list_groups as query_groups

router = APIRouter()


@router.get("", response_model=list[GroupSummary], summary="List hobby groups")
def list_groups(
    category: str | None = None,
    search: str | None = None,
    interest: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_db),
) -> list[GroupSummary]:
    query = GroupListQuery(category=category, search=search, interest=interest, page=page, page_size=page_size)
    items, total = query_groups(session, search=query.search, category=query.category, interest=query.interest, page=query.page, page_size=query.page_size)
    return items


@router.get("/{group_id}", response_model=GroupDetail, summary="Get a hobby group")
def get_group_detail(group_id: UUID, session: Session = Depends(get_db)) -> GroupDetail:
    group = get_group(session, group_id)
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return group