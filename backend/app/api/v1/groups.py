from uuid import UUID

from fastapi import APIRouter, Query

from app.schemas.common import ApiResponse, Meta
from app.schemas.groups import GroupDetail, GroupListQuery, GroupSummary

router = APIRouter()


@router.get("", response_model=ApiResponse[list[GroupSummary]], summary="List hobby groups")
def list_groups(category: str | None = None, search: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)) -> ApiResponse[list[GroupSummary]]:
    GroupListQuery(category=category, search=search, page=page, page_size=page_size)
    return ApiResponse(data=[], meta=Meta(page=page, page_size=page_size, total=0))


@router.get("/{group_id}", response_model=ApiResponse[GroupDetail], summary="Get a hobby group")
def get_group(group_id: UUID) -> ApiResponse[GroupDetail]:
    return ApiResponse(data=None, error={"code": "not_implemented", "message": f"Group {group_id} is not available in the foundation release."})