from __future__ import annotations

from typing import Literal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Event, EventInterest, Group, GroupInterest, User, UserInterest
from app.services.ai_service import AIService

TargetType = Literal["group", "event"]
IcebreakerStyle = Literal["casual", "friendly", "professional"]


class IcebreakerTargetNotFound(Exception):
    pass


class IcebreakerService:
    def __init__(self, session: Session, ai_service: AIService) -> None:
        self.session = session
        self.ai_service = ai_service

    async def generate(self, user_id: UUID, target_type: TargetType, target_id: UUID, style: IcebreakerStyle) -> str:
        user_interests = self._load_user_interests(user_id)
        target, target_interests = self._load_target(target_type, target_id)
        shared_interests = sorted(user_interests & target_interests)
        prompt_context = self._build_prompt_context(target_type, target, target_interests, shared_interests, style)
        try:
            generated = await self.ai_service.generate_icebreaker(prompt_context)
            cleaned = " ".join(generated.split())
            if 0 < len(cleaned) <= 280:
                return cleaned
        except Exception:
            pass
        return self._fallback(target_type, target, shared_interests, style)

    def _load_user_interests(self, user_id: UUID) -> set[str]:
        user = self.session.scalar(
            select(User).where(User.id == user_id).options(selectinload(User.interests).selectinload(UserInterest.interest))
        )
        if user is None:
            raise IcebreakerTargetNotFound("user not found")
        return {link.interest.name for link in user.interests if link.interest is not None}

    def _load_target(self, target_type: TargetType, target_id: UUID) -> tuple[Group | Event, set[str]]:
        if target_type == "group":
            target = self.session.scalar(
                select(Group).where(Group.id == target_id).options(selectinload(Group.interests).selectinload(GroupInterest.interest))
            )
            if target is None:
                raise IcebreakerTargetNotFound("group not found")
            return target, {link.interest.name for link in target.interests if link.interest is not None}

        target = self.session.scalar(
            select(Event).where(Event.id == target_id).options(
                selectinload(Event.interests).selectinload(EventInterest.interest),
            )
        )
        if target is None:
            raise IcebreakerTargetNotFound("event not found")
        return target, {link.interest.name for link in target.interests if link.interest is not None}

    @staticmethod
    def _build_prompt_context(target_type: TargetType, target: Group | Event, target_interests: set[str], shared_interests: list[str], style: IcebreakerStyle) -> str:
        if target_type == "group":
            target_details = f"group name={target.name}; category={target.category}; description={target.description}; location={target.location or 'not specified'}"
        else:
            target_details = f"event name={target.name}; description={target.description}; location={target.location}; starts_at={target.start_time.isoformat()}"
        return (
            "Generate exactly one short, natural conversation opener. "
            f"Style: {style}. {target_details}. "
            f"Target interests: {', '.join(sorted(target_interests)) or 'none'}. "
            f"Shared user interests: {', '.join(shared_interests) or 'none'}. "
            "Mention a shared interest only when one exists. Ask an easy question. "
            "Do not invent experiences, private user information, or facts not present in this context."
        )

    @staticmethod
    def _fallback(target_type: TargetType, target: Group | Event, shared_interests: list[str], style: IcebreakerStyle) -> str:
        subject = "group" if target_type == "group" else "event"
        if shared_interests:
            return f"{_greeting(style)} I saw you're interested in {shared_interests[0]} too. Are you joining the {target.name} {subject}?"
        return f"{_greeting(style)} What are you most looking forward to about the {target.name} {subject}?"


def _greeting(style: IcebreakerStyle) -> str:
    return {"casual": "Hey!", "friendly": "Hi there!", "professional": "Hello!"}[style]