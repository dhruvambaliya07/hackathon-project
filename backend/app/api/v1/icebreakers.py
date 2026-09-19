from fastapi import APIRouter, Depends

from app.schemas.common import ApiResponse
from app.schemas.icebreakers import IcebreakerRequest, IcebreakerResult
from app.services.icebreaker_service import IcebreakerService

router = APIRouter()


@router.post("", response_model=ApiResponse[IcebreakerResult], summary="Generate conversation icebreakers")
async def create_icebreakers(request: IcebreakerRequest, service: IcebreakerService = Depends(IcebreakerService)) -> ApiResponse[IcebreakerResult]:
    prompts = await service.generate(request.user_id, request.group_id, request.event_id, request.context)
    return ApiResponse(data=IcebreakerResult(prompts=prompts))