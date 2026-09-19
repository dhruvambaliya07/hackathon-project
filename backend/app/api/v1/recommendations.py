from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.recommendations import RecommendationItem, RecommendationRequest, RecommendationResult
from app.services.embedding_service import DeterministicEmbeddingProvider, OpenAICompatibleEmbeddingProvider, ProviderEmbeddingService, ResilientEmbeddingService
from app.services.matching_service import ScoringWeights
from app.services.recommendation_service import RecommendationService

router = APIRouter()


def get_recommendation_service(session: Session = Depends(get_db)) -> RecommendationService:
    settings = get_settings()
    primary = ProviderEmbeddingService(OpenAICompatibleEmbeddingProvider(settings))
    fallback = ProviderEmbeddingService(DeterministicEmbeddingProvider(settings.embedding_dimension))
    weights = ScoringWeights(
        semantic_similarity=settings.semantic_weight,
        interest_overlap=settings.interest_overlap_weight,
        goal_compatibility=settings.goal_compatibility_weight,
        event_relevance=settings.event_relevance_weight,
    )
    return RecommendationService(session, ResilientEmbeddingService(primary, fallback), weights=weights)


@router.post("", response_model=ApiResponse[RecommendationResult], summary="Get hobby group and event recommendations")
async def create_recommendations(request: RecommendationRequest, service: RecommendationService = Depends(get_recommendation_service)) -> ApiResponse[RecommendationResult]:
    items = await service.recommend(request.user_id, request.interest_text, request.limit)
    return ApiResponse(data=RecommendationResult(recommendations=[RecommendationItem.model_validate(item) for item in items]))