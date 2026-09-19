from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.feedback import FeedbackRequest, FeedbackResult
from app.services.feedback_service import DuplicateFeedback, FeedbackNotFound, FeedbackService

router = APIRouter()


@router.post("", response_model=FeedbackResult, status_code=201, summary="Submit recommendation feedback")
def create_feedback(request: FeedbackRequest, session: Session = Depends(get_db)) -> FeedbackResult:
    try:
        FeedbackService(session).submit(request.user_id, request.recommendation_id, request.feedback_type)
    except FeedbackNotFound as exc:
        raise HTTPException(status_code=404, detail="Recommendation was not found") from exc
    except DuplicateFeedback as exc:
        raise HTTPException(status_code=409, detail="Feedback was already recorded") from exc
    return FeedbackResult(feedback_type=request.feedback_type)