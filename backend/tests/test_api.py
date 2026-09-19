from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_openapi_contains_required_paths() -> None:
    paths = client.get("/openapi.json").json()["paths"]
    required = {
        "/api/v1/interests/analyze",
        "/api/v1/recommendations",
        "/api/v1/groups",
        "/api/v1/groups/{group_id}",
        "/api/v1/events",
        "/api/v1/events/{event_id}",
        "/api/v1/icebreakers",
        "/api/v1/feedback",
        "/api/v1/profile/{user_id}",
        "/api/v1/health",
    }
    assert required <= paths.keys()


def test_analyze_returns_predictable_envelope() -> None:
    response = client.post("/api/v1/interests/analyze", json={"text": "I enjoy photography and hiking"})
    assert response.status_code == 200
    assert set(response.json()) == {"data", "meta", "error"}
    assert response.json()["data"]["original_text"] == "I enjoy photography and hiking"


def test_groups_returns_paginated_empty_envelope() -> None:
    response = client.get("/api/v1/groups?page=2&page_size=5")
    assert response.status_code == 200
    assert response.json()["data"] == []
    assert response.json()["meta"]["page"] == 2


def test_validation_errors_are_safe_and_consistent() -> None:
    response = client.post("/api/v1/interests/analyze", json={"text": "x"})
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "validation_error"
    assert "traceback" not in response.text.lower()


def test_health_reports_database_connectivity() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "ok"
    assert response.json()["data"]["database"] == "ok"
    assert "DATABASE_URL" not in response.text


def test_unexpected_request_fields_are_rejected() -> None:
    response = client.post("/api/v1/interests/analyze", json={"text": "photography", "admin": True})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"