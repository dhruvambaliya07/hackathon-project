from __future__ import annotations

from typing import Literal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Event, EventInterest, Feedback, Group, GroupInterest, Recommendation, User, UserInterest

FeedbackType = Literal["interested", "not_interested", "already_joined", "wrong_match"]
WEIGHT_DELTAS: dict[str, float] = {"interested": 0.05, "wrong_match": -0.05}


class FeedbackNotFound(Exception):
    pass


class DuplicateFeedback(Exception):
    pass


class FeedbackService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def submit(self, user_id: UUID, recommendation_id: UUID, feedback_type: FeedbackType) -> Feedback:
        user = self.session.get(User, user_id)
        recommendation = self.session.scalar(
            select(Recommendation).where(Recommendation.id == recommendation_id, Recommendation.user_id == user_id)
        )
        if user is None or recommendation is None:
            raise FeedbackNotFound("recommendation not found")
        duplicate = self.session.scalar(
            select(Feedback).where(
                Feedback.user_id == user_id,
                Feedback.recommendation_id == recommendation_id,
                Feedback.feedback_type == feedback_type,
            )
        )
        if duplicate is not None:
            raise DuplicateFeedback("feedback already recorded")
        self._adjust_weights(user_id, recommendation.target_type, recommendation.target_id, feedback_type)
        feedback = Feedback(
            user_id=user_id,
            recommendation_id=recommendation_id,
            target_type=recommendation.target_type,
            target_id=recommendation.target_id,
            feedback_type=feedback_type,
        )
        self.session.add(feedback)
        self.session.commit()
        return feedback

    def _adjust_weights(self, user_id: UUID, target_type: str, target_id: UUID, feedback_type: FeedbackType) -> None:
        delta = WEIGHT_DELTAS.get(feedback_type)
        if delta is None:
            return
        if target_type == "group":
            links = self.session.scalars(
                select(GroupInterest).where(GroupInterest.group_id == target_id).options(selectinload(GroupInterest.interest))
            ).all()
        elif target_type == "event":
            links = self.session.scalars(
                select(EventInterest).where(EventInterest.event_id == target_id).options(selectinload(EventInterest.interest))
            ).all()
        else:
            return
        interest_ids = [link.interest_id for link in links]
        if not interest_ids:
            return
        user_links = self.session.scalars(
            select(UserInterest).where(UserInterest.user_id == user_id, UserInterest.interest_id.in_(interest_ids))
        ).all()
        for link in user_links:
            link.weight = min(1.0, max(0.0, round(link.weight + delta, 6)))
