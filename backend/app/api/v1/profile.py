from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.profile import ProfileResponse, ProfileUpdate
from app.services.profile_service import InterestNotFound, ProfileNotFound, ProfileService

router = APIRouter()


def get_profile_service(session: Session = Depends(get_db)) -> ProfileService:
    return ProfileService(session)


@router.get("/{user_id}", response_model=ProfileResponse, summary="Get a student profile")
def get_profile(user_id: UUID, service: ProfileService = Depends(get_profile_service)) -> ProfileResponse:
    try:
        return service.get(user_id)
    except ProfileNotFound as exc:
        raise HTTPException(status_code=404, detail="Profile was not found") from exc


@router.put("/{user_id}", response_model=ProfileResponse, summary="Update a student profile")
def update_profile(user_id: UUID, request: ProfileUpdate, service: ProfileService = Depends(get_profile_service)) -> ProfileResponse:
    try:
        profile = service.update(user_id, name=request.name, bio=request.bio, interests=request.interests, goals=request.goals)
    except ProfileNotFound as exc:
        raise HTTPException(status_code=404, detail="Profile was not found") from exc
    except InterestNotFound as exc:
        raise HTTPException(status_code=422, detail="One or more interests were not found") from exc
    return profile