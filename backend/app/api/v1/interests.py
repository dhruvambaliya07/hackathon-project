from fastapi import APIRouter, Depends, HTTPException

from app.schemas.common import ApiResponse
from app.schemas.interests import InterestAnalysis, InterestAnalyzeRequest
from app.services.ai_service import AIService, KeywordFallbackAIService, OpenAICompatibleProvider, StructuredAIService
from app.config import get_settings

router = APIRouter()


def get_ai_service() -> AIService:
    settings = get_settings()
    if settings.ai_api_key in {"test-key", "replace-me"}:
        return KeywordFallbackAIService()
    return StructuredAIService(OpenAICompatibleProvider(settings))


@router.post("/analyze", response_model=ApiResponse[InterestAnalysis], summary="Analyze a natural-language interest description")
async def analyze_interests(request: InterestAnalyzeRequest, service: AIService = Depends(get_ai_service)) -> ApiResponse[InterestAnalysis]:
    try:
        analysis = await service.analyze_interests(request.text)
    except Exception as exc:
        if isinstance(exc, HTTPException):
            raise
        raise HTTPException(status_code=502, detail="Interest analysis service is unavailable") from exc
    return ApiResponse(data=analysis)