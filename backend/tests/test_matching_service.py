import asyncio
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.services.embedding_service import DeterministicEmbeddingProvider, ProviderEmbeddingService
from app.services.matching_service import (
    Candidate,
    MatchingService,
    ScoringWeights,
    build_explanation_evidence,
    calculate_hybrid_score,
    cosine_similarity,
    interest_overlap,
)


def test_cosine_similarity_and_missing_embeddings() -> None:
    assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) == 1.0
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == 0.0
    assert cosine_similarity(None, [1.0]) is None
    assert cosine_similarity([0.0, 0.0], [1.0, 0.0]) is None


def test_weighted_interest_overlap_returns_evidence() -> None:
    score, matches = interest_overlap({"Photography": 1.0, "Writing": 0.5}, {"photography": 0.8, "coding": 1.0})
    assert score == 0.8 / 1.5
    assert matches == ["photography"]


def test_hybrid_score_uses_default_heuristic_weights_and_normalizes() -> None:
    breakdown = calculate_hybrid_score(
        semantic_similarity=1.0,
        interest_overlap_score=0.5,
        goal_compatibility_score=1.0,
        event_relevance_score=0.0,
        matched_interests=["photography"],
        matched_goals=["create"],
        event_connection=None,
    )
    assert breakdown.final_score == 77.5
    assert build_explanation_evidence(breakdown)["matched_interests"] == ["photography"]


def test_missing_embedding_redistributes_available_weight() -> None:
    breakdown = calculate_hybrid_score(
        semantic_similarity=None,
        interest_overlap_score=1.0,
        goal_compatibility_score=1.0,
        event_relevance_score=0.0,
        matched_interests=["programming"],
        matched_goals=["learn"],
        event_connection=None,
    )
    assert breakdown.final_score == 80.0


def test_matching_ranks_candidates_by_final_score() -> None:
    service = MatchingService(ScoringWeights(semantic_similarity=0.5, interest_overlap=0.25, goal_compatibility=0.15, event_relevance=0.1))
    candidates = [
        Candidate("group", uuid4(), "Weak", "", [0.0, 1.0], {"cooking": 1.0}),
        Candidate("group", uuid4(), "Strong", "", [1.0, 0.0], {"photography": 1.0}, frozenset({"create"})),
    ]
    scores = [service.score([1.0, 0.0], {"photography": 1.0}, {"create"}, candidate) for candidate in candidates]
    assert scores[1].final_score > scores[0].final_score


def test_event_relevance_is_bounded_and_not_date_only() -> None:
    candidate = Candidate(
        "event",
        uuid4(),
        "Workshop",
        "",
        [1.0],
        {"photography": 1.0},
        frozenset({"create"}),
        datetime.now(timezone.utc) + timedelta(days=10),
        0.8,
    )
    score = MatchingService().score([1.0], {"photography": 1.0}, {"create"}, candidate)
    assert 0 <= score.event_relevance <= 1
    assert score.event_connection == "upcoming event with matching interests"


def test_deterministic_embedding_is_cached_by_caller_and_repeatable() -> None:
    service = ProviderEmbeddingService(DeterministicEmbeddingProvider(dimension=8))
    first = asyncio.run(service.generate_embedding("photography and coding"))
    second = asyncio.run(service.generate_embedding("photography and coding"))
    assert first == second
    assert len(first) == 8
