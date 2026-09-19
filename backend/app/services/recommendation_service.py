from __future__ import annotations

from collections.abc import Mapping
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import Event, EventInterest, Group, GroupInterest, Interest, Recommendation, User, UserInterest
from app.services.ai_service import AIService
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
    def __init__(self, session: Session, embedding_service: EmbeddingService, ai_service: AIService, weights: ScoringWeights | None = None, candidate_limit: int = 100) -> None:
        self.session = session
        self.embedding_service = embedding_service
        self.ai_service = ai_service
        self.matcher = MatchingService(weights)
        self.candidate_limit = candidate_limit

    async def recommend(self, user_id: UUID | None, interest_text: str, limit: int) -> list[dict[str, object]]:
        user_interests, profile_goals = self._load_profile(user_id)
        analysis = await self.ai_service.analyze_interests(interest_text)
        self._store_analysis(user_id, analysis)
        user_embedding = await self.embedding_service.generate_embedding(interest_text)
        for item in analysis.interests:
            user_interests[item.name.lower()] = max(user_interests.get(item.name.lower(), 0.0), item.confidence)
        user_goals = set(profile_goals) | set(analysis.goals)

        candidates = self._retrieve_candidates(user_embedding)
        ranked: list[tuple[float, dict[str, object]]] = []
        for candidate in candidates:
            breakdown = self.matcher.score(user_embedding, user_interests, user_goals, candidate)
            evidence: dict[str, object] = {
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
                "matched_goals": breakdown.matched_goals,
                "explanation": deterministic_explanation(breakdown),
            }))
        ranked.sort(key=lambda item: (-item[0], str(item[1]["target_type"]), str(item[1]["target_id"])))
        results: list[dict[str, object]] = []
        stored: list[tuple[Recommendation, dict[str, object]]] = []
        seen_targets: set[tuple[str, UUID]] = set()
        for score, item in ranked[:limit]:
            target_key = (str(item["target_type"]), item["target_id"])
            if target_key in seen_targets:
                continue
            seen_targets.add(target_key)
            recommendation = Recommendation(
                user_id=user_id,
                target_type=str(item["target_type"]),
                target_id=item["target_id"],
                score=max(0.0, min(1.0, score / 100)),
                reason={"matched_interests": item["matched_interests"], "reasons": item["reasons"]},
            )
            self.session.add(recommendation)
            stored.append((recommendation, item))
        self.session.flush()
        for recommendation, item in stored:
            item["id"] = recommendation.id
            results.append(item)
        self.session.commit()
        return results

    def _load_profile(self, user_id: UUID | None) -> tuple[dict[str, float], set[str]]:
        if user_id is None:
            return {}, set()
        user = self.session.scalar(
            select(User).where(User.id == user_id).options(selectinload(User.interests).selectinload(UserInterest.interest))
        )
        if user is None:
            raise RecommendationUserNotFound("user not found")
        interests = {link.interest.name.lower(): link.weight for link in user.interests}
        goals = set(user.goals or []) | set().union(*(CATEGORY_GOALS.get(link.interest.category.lower(), frozenset()) for link in user.interests))
        return interests, goals

    def _store_analysis(self, user_id: UUID | None, analysis) -> None:
        if user_id is None:
            return
        interests = self.session.scalars(
            select(Interest).where(func.lower(Interest.name).in_([item.name.lower() for item in analysis.interests]))
        ).all()
        by_name = {interest.name.lower(): interest for interest in interests}
        user = self.session.get(User, user_id)
        if user is None:
            raise RecommendationUserNotFound("user not found")
        links = {link.interest_id: link for link in user.interests}
        for item in analysis.interests:
            interest = by_name.get(item.name.lower())
            if interest is None:
                continue
            link = links.get(interest.id)
            if link is None:
                self.session.add(UserInterest(user_id=user_id, interest_id=interest.id, weight=item.confidence, source=analysis.source))
            else:
                link.weight = max(link.weight, item.confidence)
                link.source = analysis.source
        self.session.flush()

    def _retrieve_candidates(self, user_embedding: list[float]) -> list[Candidate]:
        groups = self.session.scalars(
            select(Group)
            .options(selectinload(Group.interests).selectinload(GroupInterest.interest))
            .order_by(Group.name)
            .limit(self.candidate_limit)
        ).unique().all()
        events = self.session.scalars(
            select(Event)
            .options(
                selectinload(Event.group).selectinload(Group.interests).selectinload(GroupInterest.interest),
                selectinload(Event.interests).selectinload(EventInterest.interest),
            )
            .order_by(Event.start_time, Event.name)
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


class RecommendationUserNotFound(Exception):
    pass


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
