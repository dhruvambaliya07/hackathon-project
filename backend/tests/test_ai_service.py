import asyncio

import pytest
from fastapi.testclient import TestClient

from app.api.v1.interests import get_ai_service
from app.main import app
from app.services.ai_service import KeywordFallbackAIService, StructuredAIService


class FakeProvider:
    def __init__(self, response: str | Exception) -> None:
        self.response = response

    async def complete(self, prompt: str) -> str:
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


@pytest.fixture
def client() -> TestClient:
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_ai_service, None)


def test_normal_structured_response_and_normalization(client: TestClient) -> None:
    service = StructuredAIService(FakeProvider('{"interests":[{"name":"taking photos","confidence":0.94}],"goals":["learn"],"traits":["creative"]}'))
    app.dependency_overrides[get_ai_service] = lambda: service
    response = client.post("/api/v1/interests/analyze", json={"text": "I love taking photos"})
    assert response.status_code == 200
    assert response.json()["interests"] == [{"name": "photography", "category": "Creative", "confidence": 0.94}]
    assert response.json()["source"] == "ai"


def test_recoverable_json_wrapper_is_accepted(client: TestClient) -> None:
    service = StructuredAIService(FakeProvider('Here is the JSON:\n{"interests":[{"name":"coding","confidence":0.8}]}'))
    app.dependency_overrides[get_ai_service] = lambda: service
    response = client.post("/api/v1/interests/analyze", json={"text": "I enjoy coding"})
    assert response.status_code == 200
    assert response.json()["interests"][0]["name"] == "programming"


def test_ai_response_is_canonicalized_and_deduplicated(client: TestClient) -> None:
    service = StructuredAIService(FakeProvider(
        '{"interests":[{"name":"taking photos","confidence":0.7},{"name":"photography","confidence":0.95},{"name":"making reels","confidence":0.8}],"goals":["meet_people","meet_people"],"traits":["social"],"preferences":["beginner friendly"]}'
    ))
    app.dependency_overrides[get_ai_service] = lambda: service

    response = client.post("/api/v1/interests/analyze", json={"text": "I like photography and reels"})

    assert response.status_code == 200
    assert response.json()["interests"] == [
        {"name": "filmmaking", "category": "Creative", "confidence": 0.8},
        {"name": "photography", "category": "Creative", "confidence": 0.95},
    ]
    assert response.json()["goals"] == ["meet_people"]
    assert response.json()["preferences"] == ["beginner_friendly"]


def test_malformed_response_uses_deterministic_fallback(client: TestClient) -> None:
    service = StructuredAIService(FakeProvider("not json at all"))
    app.dependency_overrides[get_ai_service] = lambda: service
    response = client.post("/api/v1/interests/analyze", json={"text": "I enjoy photography"})
    assert response.status_code == 200
    assert response.json()["source"] == "fallback"
    assert "not json" not in response.text


def test_timeout_uses_keyword_fallback(client: TestClient) -> None:
    service = StructuredAIService(FakeProvider(TimeoutError()))
    app.dependency_overrides[get_ai_service] = lambda: service
    response = client.post("/api/v1/interests/analyze", json={"text": "I love photography and coding"})
    assert response.status_code == 200
    assert response.json()["source"] == "fallback"
    assert {item["name"] for item in response.json()["interests"]} == {"photography", "programming"}


def test_invalid_provider_schema_uses_keyword_fallback(client: TestClient) -> None:
    service = StructuredAIService(FakeProvider('{"interests":[{"name":"photography","confidence":"certain"}]}'))
    app.dependency_overrides[get_ai_service] = lambda: service
    response = client.post("/api/v1/interests/analyze", json={"text": "I enjoy photography"})
    assert response.status_code == 200
    assert response.json()["source"] == "fallback"
    assert response.json()["interests"][0]["name"] == "photography"


def test_unexpected_provider_failure_uses_keyword_fallback(client: TestClient) -> None:
    service = StructuredAIService(FakeProvider(RuntimeError("provider secret")))
    app.dependency_overrides[get_ai_service] = lambda: service
    response = client.post("/api/v1/interests/analyze", json={"text": "I enjoy photography"})
    assert response.status_code == 200
    assert response.json()["source"] == "fallback"
    assert "provider secret" not in response.text


def test_empty_and_huge_input_are_rejected(client: TestClient) -> None:
    assert client.post("/api/v1/interests/analyze", json={"text": "   "}).status_code == 422
    assert client.post("/api/v1/interests/analyze", json={"text": "x" * 2001}).status_code == 422


def test_fallback_is_deterministic_and_marked() -> None:
    first = asyncio.run(KeywordFallbackAIService().analyze_interests("building websites and making reels"))
    second = asyncio.run(KeywordFallbackAIService().analyze_interests("building websites and making reels"))
    assert first == second
    assert first.source == "fallback"
    assert {item.name for item in first.interests} == {"filmmaking", "web development"}