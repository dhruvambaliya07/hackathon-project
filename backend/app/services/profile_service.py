from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session, selectinload

from app.models import Event, Feedback, Group, Interest, User, UserInterest
from app.schemas.events import EventSummary
from app.schemas.profile import ProfileEvent, ProfileGroup, ProfileInterest, ProfileResponse, ProfileUser
from app.schemas.groups import GroupSummary

GOAL_BY_CATEGORY = {
    "technology": "learn",
    "creative": "create",
    "social": "meet_people",
    "lifestyle": "stay_active",
    "entertainment": "meet_people",
    "business": "build_career",
}
TRAIT_BY_CATEGORY = {
    "technology": "technical",
    "creative": "creative",
    "social": "collaborative",
    "lifestyle": "active",
    "entertainment": "creative",
    "business": "entrepreneurial",
}


class ProfileNotFound(Exception):
    pass


class InterestNotFound(Exception):
    pass


class ProfileService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, user_id: UUID) -> ProfileResponse:
        user = self._load_user(user_id)
        return self._response(user)

    def update(self, user_id: UUID, *, name: str | None, bio: str | None, interests: list[str] | None, goals: list[str] | None) -> ProfileResponse:
        user = self._load_user(user_id)
        if name is not None:
            user.name = name.strip()
        if bio is not None:
            user.bio = bio
        if interests is not None:
            self._replace_interests(user, interests)
        if goals is not None:
            user.goals = list(dict.fromkeys(goal.strip() for goal in goals if goal.strip()))
        user.traits = self._derive_traits(user)
        self.session.commit()
        return self.get(user_id)

    def _load_user(self, user_id: UUID) -> User:
        user = self.session.scalar(
            select(User).where(User.id == user_id).options(selectinload(User.interests).selectinload(UserInterest.interest))
        )
        if user is None:
            raise ProfileNotFound("user not found")
        return user

    def _replace_interests(self, user: User, names: list[str]) -> None:
        normalized = list(dict.fromkeys(name.strip().lower() for name in names if name.strip()))
        interests = self.session.scalars(select(Interest).where(func.lower(Interest.name).in_(normalized))).all()
        by_name = {interest.name.lower(): interest for interest in interests}
        if len(by_name) != len(normalized):
            raise InterestNotFound("one or more interests were not found")
        self.session.execute(delete(UserInterest).where(UserInterest.user_id == user.id))
        user.interests = [UserInterest(user_id=user.id, interest_id=by_name[name].id, weight=1.0, source="profile") for name in normalized]
        self.session.flush()

    @staticmethod
    def _derive_traits(user: User) -> list[str]:
        traits = {TRAIT_BY_CATEGORY.get(link.interest.category.lower()) for link in user.interests if link.interest is not None}
        return sorted(trait for trait in traits if trait is not None)

    def _response(self, user: User) -> ProfileResponse:
        feedback = self.session.scalars(
            select(Feedback).where(Feedback.user_id == user.id, Feedback.feedback_type == "interested")
        ).all()
        group_ids = [item.target_id for item in feedback if item.target_type == "group"]
        event_ids = [item.target_id for item in feedback if item.target_type == "event"]
        groups = self.session.scalars(select(Group).where(Group.id.in_(group_ids)).order_by(Group.name)).all() if group_ids else []
        events = self.session.scalars(select(Event).where(Event.id.in_(event_ids)).order_by(Event.start_time)).all() if event_ids else []
        goals = list(user.goals or []) or sorted({GOAL_BY_CATEGORY.get(link.interest.category.lower()) for link in user.interests if link.interest is not None} - {None})
        return ProfileResponse(
            user=ProfileUser.model_validate(user, from_attributes=True),
            interests=[ProfileInterest(id=link.interest.id, name=link.interest.name, category=link.interest.category, weight=link.weight) for link in user.interests if link.interest is not None],
            goals=goals,
            traits=list(user.traits or self._derive_traits(user)),
            saved_groups=[ProfileGroup.model_validate(group, from_attributes=True) for group in groups],
            interested_events=[ProfileEvent(id=event.id, group_id=event.group_id, title=event.name, description=event.description, starts_at=event.start_time, ends_at=event.end_time, location=event.location) for event in events],
        )
