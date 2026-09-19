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
    assert response.json()["data"]["interests"] == [{"name": "photography", "confidence": 0.94}]
    assert response.json()["data"]["source"] == "ai"


def test_recoverable_json_wrapper_is_accepted(client: TestClient) -> None:
    service = StructuredAIService(FakeProvider('Here is the JSON:\n{"interests":[{"name":"coding","confidence":0.8}]}'))
    app.dependency_overrides[get_ai_service] = lambda: service
    response = client.post("/api/v1/interests/analyze", json={"text": "I enjoy coding"})
    assert response.status_code == 200
    assert response.json()["data"]["interests"][0]["name"] == "programming"


def test_malformed_response_returns_controlled_502(client: TestClient) -> None:
    service = StructuredAIService(FakeProvider("not json at all"))
    app.dependency_overrides[get_ai_service] = lambda: service
    response = client.post("/api/v1/interests/analyze", json={"text": "I enjoy photography"})
    assert response.status_code == 502
    assert response.json()["error"]["code"] == "http_error"
    assert "not json" not in response.text


def test_timeout_uses_keyword_fallback(client: TestClient) -> None:
    service = StructuredAIService(FakeProvider(TimeoutError()))
    app.dependency_overrides[get_ai_service] = lambda: service
    response = client.post("/api/v1/interests/analyze", json={"text": "I love photography and coding"})
    assert response.status_code == 200
    assert response.json()["data"]["source"] == "fallback"
    assert {item["name"] for item in response.json()["data"]["interests"]} == {"photography", "programming"}


def test_empty_and_huge_input_are_rejected(client: TestClient) -> None:
    assert client.post("/api/v1/interests/analyze", json={"text": "   "}).status_code == 422
    assert client.post("/api/v1/interests/analyze", json={"text": "x" * 2001}).status_code == 422


def test_fallback_is_deterministic_and_marked() -> None:
    first = asyncio.run(KeywordFallbackAIService().analyze_interests("building websites and making reels"))
    second = asyncio.run(KeywordFallbackAIService().analyze_interests("building websites and making reels"))
    assert first == second
    assert first.source == "fallback"
    assert {item.name for item in first.interests} == {"filmmaking", "web development"}