from uuid import UUID

from fastapi import APIRouter

from app.schemas.common import ApiResponse
from app.schemas.profile import ProfileResponse, ProfileUpdate

router = APIRouter()


@router.get("/{user_id}", response_model=ApiResponse[ProfileResponse], summary="Get a student profile")
def get_profile(user_id: UUID) -> ApiResponse[ProfileResponse]:
    return ApiResponse(data=None, error={"code": "not_implemented", "message": f"Profile {user_id} is not available in the foundation release."})


@router.put("/{user_id}", response_model=ApiResponse[ProfileResponse], summary="Update a student profile")
def update_profile(user_id: UUID, request: ProfileUpdate) -> ApiResponse[ProfileResponse]:
    return ApiResponse(data=None, error={"code": "not_implemented", "message": f"Profile {user_id} is not available in the foundation release."})