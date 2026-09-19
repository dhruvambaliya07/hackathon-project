from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.rate_limit import limit_icebreakers
from app.api.v1.interests import get_ai_service
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.icebreakers import IcebreakerRequest, IcebreakerResult
from app.services.ai_service import AIService
from app.services.icebreaker_service import IcebreakerService, IcebreakerTargetNotFound

router = APIRouter()


def get_icebreaker_service(session: Session = Depends(get_db), ai_service: AIService = Depends(get_ai_service)) -> IcebreakerService:
    return IcebreakerService(session, ai_service)


@router.post("", response_model=ApiResponse[IcebreakerResult], summary="Generate a personalized conversation icebreaker")
async def create_icebreaker(request: IcebreakerRequest, _: None = Depends(limit_icebreakers), service: IcebreakerService = Depends(get_icebreaker_service)) -> ApiResponse[IcebreakerResult]:
    try:
        icebreaker = await service.generate(request.user_id, request.target_type, request.target_id, request.style)
    except IcebreakerTargetNotFound as exc:
        raise HTTPException(status_code=404, detail="Icebreaker target or user was not found") from exc
    return ApiResponse(data=IcebreakerResult(icebreaker=icebreaker, style=request.style))
