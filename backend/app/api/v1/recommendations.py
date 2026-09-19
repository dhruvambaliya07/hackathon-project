from fastapi import APIRouter, Depends

from app.schemas.common import ApiResponse
from app.schemas.recommendations import RecommendationItem, RecommendationRequest, RecommendationResult
from app.services.recommendation_service import RecommendationService

router = APIRouter()


def get_recommendation_service() -> RecommendationService:
    return RecommendationService()


@router.post("", response_model=ApiResponse[RecommendationResult], summary="Get hobby group and event recommendations")
async def create_recommendations(request: RecommendationRequest, service: RecommendationService = Depends(get_recommendation_service)) -> ApiResponse[RecommendationResult]:
    items = await service.recommend(request.user_id, request.interest_text, request.limit)
    return ApiResponse(data=RecommendationResult(recommendations=[RecommendationItem.model_validate(item) for item in items]))