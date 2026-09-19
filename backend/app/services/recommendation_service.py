from __future__ import annotations

from collections.abc import Mapping
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Event, EventInterest, Group, GroupInterest, User, UserInterest
from app.services.ai_service import fallback_analysis
from app.services.embedding_service import EmbeddingService
from app.services.matching_service import Candidate, MatchingService, ScoringWeights, deterministic_explanation

CATEGORY_GOALS: Mapping[str, frozenset[str]] = {
    "technology": frozenset({"learn", "build_career"}),
    "creative": frozenset({"create", "learn"}),
    "social": frozenset({"meet_people", "help_community"}),
    "lifestyle": frozenset({"stay_active", "relax"}),
    "entertainment": frozenset({"create", "meet_people"}),
    "business": frozenset({"build_career", "learn"}),
}


class RecommendationService:
    def __init__(self, session: Session, embedding_service: EmbeddingService, weights: ScoringWeights | None = None, candidate_limit: int = 100) -> None:
        self.session = session
        self.embedding_service = embedding_service
        self.matcher = MatchingService(weights)
        self.candidate_limit = candidate_limit

    async def recommend(self, user_id: UUID | None, interest_text: str, limit: int) -> list[dict[str, object]]:
        user_embedding = await self.embedding_service.generate_embedding(interest_text)
        user_interests, profile_goals = self._load_profile(user_id)
        analysis = fallback_analysis(interest_text)
        for item in analysis.interests:
            user_interests[item.name] = max(user_interests.get(item.name, 0.0), item.confidence)
        user_goals = set(profile_goals) | set(analysis.goals)

        candidates = self._retrieve_candidates(user_embedding)
        ranked: list[tuple[float, dict[str, object]]] = []
        for candidate in candidates:
            breakdown = self.matcher.score(user_embedding, user_interests, user_goals, candidate)
            evidence = {
                "matched_interests": breakdown.matched_interests,
                "matched_goals": breakdown.matched_goals,
                "event_connection": breakdown.event_connection,
                "semantic_relevance": round(breakdown.semantic_similarity, 3),
            }
            reasons = _reason_list(evidence)
            ranked.append((breakdown.final_score, {
                "id": candidate.target_id,
                "type": candidate.target_type,
                "target_type": candidate.target_type,
                "target_id": candidate.target_id,
                "title": candidate.title,
                "description": candidate.description,
                "score": round(breakdown.final_score, 1),
                "matched_interests": breakdown.matched_interests,
                "reasons": reasons,
                "explanation": deterministic_explanation(breakdown),
            }))
        ranked.sort(key=lambda item: (-item[0], str(item[1]["target_id"])))
        return [item for _score, item in ranked[:limit]]

    def _load_profile(self, user_id: UUID | None) -> tuple[dict[str, float], set[str]]:
        if user_id is None:
            return {}, set()
        user = self.session.scalar(
            select(User).where(User.id == user_id).options(selectinload(User.interests).selectinload(UserInterest.interest))
        )
        if user is None:
            return {}, set()
        interests = {link.interest.name.lower(): link.weight for link in user.interests}
        goals = set().union(*(CATEGORY_GOALS.get(link.interest.category.lower(), frozenset()) for link in user.interests))
        return interests, goals

    def _retrieve_candidates(self, user_embedding: list[float]) -> list[Candidate]:
        groups = self.session.scalars(
            select(Group)
            .options(selectinload(Group.interests).selectinload(GroupInterest.interest))
            .order_by(Group.embedding.cosine_distance(user_embedding).nullslast(), Group.name)
            .limit(self.candidate_limit)
        ).unique().all()
        events = self.session.scalars(
            select(Event)
            .options(
                selectinload(Event.group).selectinload(Group.interests).selectinload(GroupInterest.interest),
                selectinload(Event.interests).selectinload(EventInterest.interest),
            )
            .order_by(Event.embedding.cosine_distance(user_embedding).nullslast(), Event.start_time)
            .limit(self.candidate_limit)
        ).unique().all()
        return [self._group_candidate(group) for group in groups] + [self._event_candidate(event) for event in events]

    def _group_candidate(self, group: Group) -> Candidate:
        interests = {link.interest.name.lower(): link.weight for link in group.interests}
        return Candidate(
            target_type="group",
            target_id=group.id,
            title=group.name,
            description=group.description,
            embedding=group.embedding,
            interests=interests,
            goals=CATEGORY_GOALS.get(group.category.lower(), frozenset()),
            group_relevance=0.0,
        )

    def _event_candidate(self, event: Event) -> Candidate:
        interests = {link.interest.name.lower(): link.weight for link in event.interests}
        group_interests = {link.interest.name.lower(): link.weight for link in event.group.interests}
        return Candidate(
            target_type="event",
            target_id=event.id,
            title=event.name,
            description=event.description,
            embedding=event.embedding,
            interests=interests,
            goals=CATEGORY_GOALS.get(event.group.category.lower(), frozenset()),
            start_time=event.start_time,
            group_relevance=min(1.0, sum(group_interests.values()) / 5),
        )


def _reason_list(evidence: dict[str, object]) -> list[str]:
    reasons: list[str] = []
    matched_interests = evidence["matched_interests"]
    matched_goals = evidence["matched_goals"]
    if matched_interests:
        reasons.append("Matched interests: " + ", ".join(str(value) for value in matched_interests))
    if matched_goals:
        reasons.append("Matched goals: " + ", ".join(str(value).replace("_", " ") for value in matched_goals))
    if evidence["event_connection"]:
        reasons.append(str(evidence["event_connection"]))
    reasons.append(f"Semantic relevance: {float(evidence['semantic_relevance']):.2f}")
    return reasons
