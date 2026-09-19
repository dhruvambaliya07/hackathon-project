import asyncio
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.api.v1.recommendations import get_recommendation_service
from app.schemas.interests import AnalyzedInterest, InterestAnalysis
from app.services.ai_service import KeywordFallbackAIService
from app.services.embedding_service import EmbeddingService
from app.services.matching_service import Candidate
from app.services.recommendation_service import RecommendationService


class MemorySession:
    def __init__(self) -> None:
        self.records = []

    def add(self, record) -> None:
        self.records.append(record)

    def flush(self) -> None:
        for record in self.records:
            if getattr(record, "id", None) is None:
                record.id = uuid4()

    def commit(self) -> None:
        return None


class FakeAI:
    def __init__(self, failure: Exception | None = None) -> None:
        self.failure = failure

    async def analyze_interests(self, text: str) -> InterestAnalysis:
        if self.failure:
            raise self.failure
        return InterestAnalysis(
            original_text=text,
            interests=[AnalyzedInterest(name="Photography", confidence=0.9)],
            source="ai",
        )

    async def generate_icebreaker(self, context: str) -> str:
        return "Hello"


class FakeEmbedding(EmbeddingService):
    async def generate_embedding(self, text: str) -> list[float]:
        return [1.0, 0.0]


def make_service(candidates: list[Candidate], ai: FakeAI | None = None) -> RecommendationService:
    service = RecommendationService(MemorySession(), FakeEmbedding(), ai or FakeAI())
    service._load_profile = lambda user_id: ({"photography": 1.0}, {"create"})  # type: ignore[method-assign]
    service._store_analysis = lambda user_id, analysis: None  # type: ignore[method-assign]
    service._retrieve_candidates = lambda embedding: candidates  # type: ignore[method-assign]
    return service


def candidate(title: str, interest: str, embedding: list[float] | None, target_type: str = "group") -> Candidate:
    return Candidate(target_type, uuid4(), title, f"{title} description", embedding, {interest: 1.0})


def test_recommendations_rank_matches_and_apply_limit() -> None:
    service = make_service([
        candidate("Cooking", "cooking", [0.0, 1.0]),
        candidate("Photography", "photography", [1.0, 0.0]),
    ])

    results = asyncio.run(service.recommend(uuid4(), "I enjoy photography", 1))

    assert len(results) == 1
    assert results[0]["title"] == "Photography"
    assert results[0]["matched_interests"] == ["photography"]
    assert UUID(str(results[0]["id"]))


def test_recommendations_handle_no_match_and_missing_embedding() -> None:
    service = make_service([
        candidate("Unknown", "cooking", None),
    ])

    results = asyncio.run(service.recommend(uuid4(), "I enjoy photography", 10))

    assert len(results) == 1
    assert results[0]["matched_interests"] == []
    assert results[0]["reasons"]


def test_recommendations_return_empty_for_no_available_candidates() -> None:
    service = make_service([])

    assert asyncio.run(service.recommend(uuid4(), "I enjoy photography", 10)) == []


def test_keyword_fallback_is_deterministic_for_recommendation_input() -> None:
    service = RecommendationService(MemorySession(), FakeEmbedding(), KeywordFallbackAIService())
    service._load_profile = lambda user_id: ({}, set())  # type: ignore[method-assign]
    service._store_analysis = lambda user_id, analysis: None  # type: ignore[method-assign]
    service._retrieve_candidates = lambda embedding: [candidate("Photography", "photography", [1.0, 0.0])]  # type: ignore[method-assign]

    first = asyncio.run(service.recommend(uuid4(), "I love photography", 10))
    second = asyncio.run(service.recommend(uuid4(), "I love photography", 10))

    assert first[0]["matched_interests"] == second[0]["matched_interests"] == ["photography"]


def test_ai_failure_returns_controlled_api_error() -> None:
    class FailingService:
        async def recommend(self, user_id, interest_text, limit):
            raise RuntimeError("provider secret")

    app.dependency_overrides[get_recommendation_service] = lambda: FailingService()
    try:
        response = TestClient(app).post(
            "/api/v1/recommendations",
            json={"user_id": str(uuid4()), "interest_text": "photography"},
        )
    finally:
        app.dependency_overrides.pop(get_recommendation_service, None)

    assert response.status_code == 502
    assert "provider secret" not in response.text
