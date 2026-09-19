from fastapi import APIRouter

from app.schemas.common import ApiResponse
from app.schemas.feedback import FeedbackRequest, FeedbackResult

router = APIRouter()


@router.post("", response_model=ApiResponse[FeedbackResult], status_code=201, summary="Submit recommendation feedback")
def create_feedback(request: FeedbackRequest) -> ApiResponse[FeedbackResult]:
    return ApiResponse(data=FeedbackResult())