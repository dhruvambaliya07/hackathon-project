from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from math import sqrt
from typing import Mapping, Sequence
from uuid import UUID


@dataclass(frozen=True)
class ScoringWeights:
    semantic_similarity: float = 0.50
    interest_overlap: float = 0.25
    goal_compatibility: float = 0.15
    event_relevance: float = 0.10

    def __post_init__(self) -> None:
        values = (self.semantic_similarity, self.interest_overlap, self.goal_compatibility, self.event_relevance)
        if any(value < 0 for value in values) or not 0.999 <= sum(values) <= 1.001:
            raise ValueError("scoring weights must be non-negative and sum to 1")


@dataclass(frozen=True)
class ScoreBreakdown:
    final_score: float
    semantic_similarity: float
    interest_overlap: float
    goal_compatibility: float
    event_relevance: float
    matched_interests: list[str] = field(default_factory=list)
    matched_goals: list[str] = field(default_factory=list)
    event_connection: str | None = None


@dataclass(frozen=True)
class Candidate:
    target_type: str
    target_id: UUID
    title: str
    description: str
    embedding: Sequence[float] | None
    interests: Mapping[str, float]
    goals: frozenset[str] = frozenset()
    start_time: datetime | None = None
    group_relevance: float = 0.0


class MatchingService:
    def __init__(self, weights: ScoringWeights | None = None) -> None:
        self.weights = weights or ScoringWeights()

    def score(self, user_embedding: list[float] | None, user_interests: Mapping[str, float], user_goals: set[str], candidate: Candidate) -> ScoreBreakdown:
        semantic = cosine_similarity(user_embedding, candidate.embedding)
        overlap, matched_interests = interest_overlap(user_interests, candidate.interests)
        goal_score, matched_goals = goal_compatibility(user_goals, set(candidate.goals))
        event_score, event_connection = event_relevance(candidate, overlap)
        return calculate_hybrid_score(
            semantic_similarity=semantic,
            interest_overlap_score=overlap,
            goal_compatibility_score=goal_score,
            event_relevance_score=event_score,
            matched_interests=matched_interests,
            matched_goals=matched_goals,
            event_connection=event_connection,
            weights=self.weights,
        )


def cosine_similarity(left: Sequence[float] | None, right: Sequence[float] | None) -> float | None:
    if left is None or right is None or len(left) == 0 or len(right) == 0 or len(left) != len(right):
        return None
    left_norm = sqrt(sum(value * value for value in left))
    right_norm = sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return None
    return max(0.0, min(1.0, sum(a * b for a, b in zip(left, right, strict=True)) / (left_norm * right_norm)))


def interest_overlap(user: Mapping[str, float], candidate: Mapping[str, float]) -> tuple[float, list[str]]:
    normalized_user = {key.strip().lower(): max(0.0, value) for key, value in user.items()}
    normalized_candidate = {key.strip().lower(): max(0.0, value) for key, value in candidate.items()}
    denominator = sum(normalized_user.values())
    if denominator == 0:
        return 0.0, []
    matches = sorted(normalized_user.keys() & normalized_candidate.keys())
    score = sum(min(normalized_user[key], normalized_candidate[key]) for key in matches) / denominator
    return max(0.0, min(1.0, score)), matches


def goal_compatibility(user_goals: set[str], candidate_goals: set[str]) -> tuple[float, list[str]]:
    if not user_goals:
        return 0.0, []
    matches = sorted(user_goals & candidate_goals)
    return len(matches) / len(user_goals), matches


def event_relevance(candidate: Candidate, interest_score: float) -> tuple[float, str | None]:
    if candidate.target_type != "event":
        return 0.0, None
    if candidate.start_time is None:
        return min(1.0, (interest_score + candidate.group_relevance) / 2), "event has no scheduled date"
    now = datetime.now(timezone.utc)
    start_time = candidate.start_time if candidate.start_time.tzinfo else candidate.start_time.replace(tzinfo=timezone.utc)
    days_until = (start_time - now).total_seconds() / 86400
    upcoming_score = 1.0 if days_until >= 0 else 0.0
    if 0 <= days_until <= 30:
        upcoming_score = 0.8 + (days_until / 30) * 0.2
    score = (upcoming_score * 0.4) + (interest_score * 0.35) + (candidate.group_relevance * 0.25)
    connection = "upcoming event with matching interests" if days_until >= 0 and interest_score > 0 else "event relevance based on schedule and group fit"
    return max(0.0, min(1.0, score)), connection


def calculate_hybrid_score(
    *,
    semantic_similarity: float | None,
    interest_overlap_score: float,
    goal_compatibility_score: float,
    event_relevance_score: float,
    matched_interests: list[str],
    matched_goals: list[str],
    event_connection: str | None,
    weights: ScoringWeights | None = None,
) -> ScoreBreakdown:
    scoring_weights = weights or ScoringWeights()
    components = {
        "semantic_similarity": semantic_similarity,
        "interest_overlap": interest_overlap_score,
        "goal_compatibility": goal_compatibility_score,
        "event_relevance": event_relevance_score,
    }
    available_weights = {name: weight for name, weight in {
        "semantic_similarity": scoring_weights.semantic_similarity,
        "interest_overlap": scoring_weights.interest_overlap,
        "goal_compatibility": scoring_weights.goal_compatibility,
        "event_relevance": scoring_weights.event_relevance,
    }.items() if components[name] is not None}
    weight_total = sum(available_weights.values()) or 1.0
    score = sum(float(components[name] or 0.0) * weight for name, weight in available_weights.items()) / weight_total
    return ScoreBreakdown(
        final_score=max(0.0, min(100.0, score * 100)),
        semantic_similarity=float(semantic_similarity or 0.0),
        interest_overlap=interest_overlap_score,
        goal_compatibility=goal_compatibility_score,
        event_relevance=event_relevance_score,
        matched_interests=matched_interests,
        matched_goals=matched_goals,
        event_connection=event_connection,
    )


def build_explanation_evidence(breakdown: ScoreBreakdown) -> dict[str, object]:
    return {
        "matched_interests": breakdown.matched_interests,
        "matched_goals": breakdown.matched_goals,
        "event_connection": breakdown.event_connection,
        "semantic_relevance": round(breakdown.semantic_similarity, 3),
    }


def deterministic_explanation(breakdown: ScoreBreakdown) -> str:
    evidence = build_explanation_evidence(breakdown)
    parts: list[str] = []
    if evidence["matched_interests"]:
        parts.append("Matches " + ", ".join(str(value) for value in evidence["matched_interests"]))
    if evidence["matched_goals"]:
        parts.append("supports " + ", ".join(str(value).replace("_", " ") for value in evidence["matched_goals"]))
    if evidence["event_connection"]:
        parts.append(str(evidence["event_connection"]))
    if float(evidence["semantic_relevance"]) > 0:
        parts.append(f"semantic relevance {float(evidence['semantic_relevance']):.2f}")
    return "; ".join(parts) if parts else "Recommended from available profile and content signals."


class StubMatchingService:
    async def match(self, user_id: UUID | None, interest_text: str, limit: int) -> list[dict[str, object]]:
        return []
