from collections.abc import Generator
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.icebreakers import get_icebreaker_service
from app.api.v1.interests import get_ai_service
from app.api.v1.recommendations import get_recommendation_service
from app.config import get_settings
from app.db.session import SessionLocal, get_db
from app.main import app
from app.models import Group, User
from app.schemas.interests import AnalyzedInterest, InterestAnalysis
from app.seed import seed_database, stable_id
from app.services.embedding_service import EmbeddingService
from app.services.icebreaker_service import IcebreakerService
from app.services.recommendation_service import RecommendationService

pytestmark = pytest.mark.skipif(
    not get_settings().database_url.startswith(("postgres://", "postgresql://", "postgresql+")),
    reason="end-to-end flow requires PostgreSQL",
)


class JourneyAI:
    async def analyze_interests(self, text: str) -> InterestAnalysis:
        return InterestAnalysis(
            original_text=text,
            interests=[AnalyzedInterest(name="Photography", confidence=0.95)],
            goals=["create"],
            traits=["creative"],
            source="ai",
        )

    async def generate_icebreaker(self, context: str) -> str:
        assert "Photography" in context
        return "What kind of photography do you enjoy most?"


class JourneyEmbedding(EmbeddingService):
    async def generate_embedding(self, text: str) -> list[float]:
        return [1.0] * 1536


@pytest.fixture
def journey_client() -> Generator[tuple[TestClient, User], None, None]:
    try:
        with SessionLocal() as session:
            session.scalar(select(Group.id))
            seed_database(session)
            user = session.get(User, stable_id("user", "maya.shah@example.test"))
            assert user is not None
    except SQLAlchemyError as exc:
        pytest.skip(f"PostgreSQL schema is unavailable: {exc}")

    ai = JourneyAI()
    embedding = JourneyEmbedding()

    def override_db() -> Generator[Session, None, None]:
        with SessionLocal() as session:
            yield session

    def recommendation_service() -> Generator[RecommendationService, None, None]:
        session = SessionLocal()
        try:
            yield RecommendationService(session, embedding, ai)
        finally:
            session.close()

    def icebreaker_service() -> Generator[IcebreakerService, None, None]:
        session = SessionLocal()
        try:
            yield IcebreakerService(session, ai)
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_ai_service] = lambda: ai
    app.dependency_overrides[get_recommendation_service] = recommendation_service
    app.dependency_overrides[get_icebreaker_service] = icebreaker_service
    try:
        yield TestClient(app), user
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_ai_service, None)
        app.dependency_overrides.pop(get_recommendation_service, None)
        app.dependency_overrides.pop(get_icebreaker_service, None)


def test_complete_profile_to_feedback_journey(journey_client) -> None:
    client, user = journey_client

    assert client.get(f"/api/v1/profile/{user.id}").status_code == 200
    analysis = client.post("/api/v1/interests/analyze", json={"text": "I love taking photos"})
    assert analysis.status_code == 200
    assert analysis.json()["data"]["interests"][0]["name"] == "Photography"

    recommendations = client.post(
        "/api/v1/recommendations",
        json={"user_id": str(user.id), "interest_text": "I love taking photos", "limit": 1},
    )
    assert recommendations.status_code == 200
    item = recommendations.json()["data"]["recommendations"][0]
    assert UUID(item["id"])
    assert item["reasons"]
    assert item["matched_interests"]

    target_path = f"/api/v1/groups/{item['target_id']}" if item["target_type"] == "group" else f"/api/v1/events/{item['target_id']}"
    assert client.get(target_path).status_code == 200

    icebreaker = client.post(
        "/api/v1/icebreakers",
        json={"user_id": str(user.id), "target_type": item["target_type"], "target_id": item["target_id"], "style": "casual"},
    )
    assert icebreaker.status_code == 200
    assert icebreaker.json()["data"]["icebreaker"]

    feedback = client.post(
        "/api/v1/feedback",
        json={"user_id": str(user.id), "recommendation_id": item["id"], "feedback_type": "interested"},
    )
    assert feedback.status_code == 201

    final_profile = client.get(f"/api/v1/profile/{user.id}")
    assert final_profile.status_code == 200
    state = final_profile.json()["data"]
    assert any(interest["name"] == "Photography" for interest in state["interests"])
    if item["target_type"] == "group":
        assert any(group["id"] == item["target_id"] for group in state["saved_groups"])
    else:
        assert any(event["id"] == item["target_id"] for event in state["interested_events"])
