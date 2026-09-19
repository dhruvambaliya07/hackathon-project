from fastapi import APIRouter, Depends

from app.schemas.common import ApiResponse
from app.schemas.interests import InterestAnalysis, InterestAnalyzeRequest
from app.services.ai_service import AIService, StubAIService

router = APIRouter()


def get_ai_service() -> AIService:
    return StubAIService()


@router.post("/analyze", response_model=ApiResponse[InterestAnalysis], summary="Analyze a natural-language interest description")
async def analyze_interests(request: InterestAnalyzeRequest, service: AIService = Depends(get_ai_service)) -> ApiResponse[InterestAnalysis]:
    interests = await service.analyze_interests(request.text)
    return ApiResponse(data=InterestAnalysis(original_text=request.text, interests=interests))