from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.recommendations import RecommendationItem, RecommendationRequest, RecommendationResult
from app.services.embedding_service import DeterministicEmbeddingProvider, OpenAICompatibleEmbeddingProvider, ProviderEmbeddingService, ResilientEmbeddingService
from app.services.ai_service import AIService
from app.api.v1.interests import get_ai_service
from app.services.matching_service import ScoringWeights
from app.services.recommendation_service import RecommendationService, RecommendationUserNotFound

router = APIRouter()


def get_recommendation_service(session: Session = Depends(get_db), ai_service: AIService = Depends(get_ai_service)) -> RecommendationService:
    settings = get_settings()
    primary = ProviderEmbeddingService(OpenAICompatibleEmbeddingProvider(settings))
    fallback = ProviderEmbeddingService(DeterministicEmbeddingProvider(settings.embedding_dimension))
    weights = ScoringWeights(
        semantic_similarity=settings.semantic_weight,
        interest_overlap=settings.interest_overlap_weight,
        goal_compatibility=settings.goal_compatibility_weight,
        event_relevance=settings.event_relevance_weight,
    )
    return RecommendationService(session, ResilientEmbeddingService(primary, fallback), ai_service, weights=weights)


@router.post("", response_model=ApiResponse[RecommendationResult], summary="Get hobby group and event recommendations")
async def create_recommendations(request: RecommendationRequest, service: RecommendationService = Depends(get_recommendation_service)) -> ApiResponse[RecommendationResult]:
    try:
        items = await service.recommend(request.user_id, request.interest_text, request.limit)
    except RecommendationUserNotFound as exc:
        raise HTTPException(status_code=404, detail="User was not found") from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Recommendation storage is temporarily unavailable") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Recommendation providers are unavailable") from exc
    return ApiResponse(data=RecommendationResult(recommendations=[RecommendationItem.model_validate(item) for item in items]))