from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.session import SessionLocal, get_db
from app.main import app
from app.models import Event, Group, Interest, User
from app.seed import INTEREST_DATA, seed_database


pytestmark = pytest.mark.skipif(
    not get_settings().database_url.startswith(("postgres://", "postgresql://", "postgresql+")),
    reason="catalog API integration tests require PostgreSQL",
)


@pytest.fixture
def catalog_client() -> Generator[TestClient, None, None]:
    try:
        with SessionLocal() as session:
            session.scalar(select(Group.id))
            seed_database(session)
    except SQLAlchemyError as exc:
        pytest.skip(f"PostgreSQL schema is unavailable: {exc}")

    def override_db() -> Generator[Session, None, None]:
        with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_list_groups_and_pagination(catalog_client: TestClient) -> None:
    response = catalog_client.get("/api/v1/groups?page=2&page_size=5")
    assert response.status_code == 200
    assert len(response.json()) == 5


def test_search_and_filter_groups(catalog_client: TestClient) -> None:
    response = catalog_client.get("/api/v1/groups?search=photography&category=creative&interest=Photography")
    assert response.status_code == 200
    assert response.json()
    assert all("photography" in item["name"].lower() or "photography" in item["description"].lower() for item in response.json())


def test_get_group_includes_interests_and_upcoming_events(catalog_client: TestClient) -> None:
    group_id = catalog_client.get("/api/v1/groups").json()[0]["id"]
    response = catalog_client.get(f"/api/v1/groups/{group_id}")
    assert response.status_code == 200
    assert response.json()["interests"]
    assert response.json()["upcoming_events"]


def test_missing_group_returns_404(catalog_client: TestClient) -> None:
    response = catalog_client.get("/api/v1/groups/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_list_and_filter_events(catalog_client: TestClient) -> None:
    response = catalog_client.get("/api/v1/events?page=1&page_size=10&category=Technology")
    assert response.status_code == 200
    assert 0 < len(response.json()) <= 10
    group_id = response.json()[0]["group_id"]
    filtered = catalog_client.get(f"/api/v1/events?group_id={group_id}")
    assert filtered.status_code == 200
    assert all(item["group_id"] == group_id for item in filtered.json())


def test_get_event_includes_group_interests_and_related_events(catalog_client: TestClient) -> None:
    event_id = catalog_client.get("/api/v1/events?page_size=1").json()[0]["id"]
    response = catalog_client.get(f"/api/v1/events/{event_id}")
    assert response.status_code == 200
    assert response.json()["group"]
    assert response.json()["interests"]
    assert response.json()["related_events"]


def test_missing_event_and_invalid_uuid(catalog_client: TestClient) -> None:
    assert catalog_client.get("/api/v1/events/00000000-0000-0000-0000-000000000000").status_code == 404
    assert catalog_client.get("/api/v1/events/not-a-uuid").status_code == 422


def test_seed_is_idempotent(catalog_client: TestClient) -> None:
    with SessionLocal() as session:
        seed_database(session)
        seed_database(session)
        assert session.query(Interest).count() == len(INTEREST_DATA)
        assert session.query(Group).count() == 20
        assert session.query(Event).count() == 40
        assert session.query(User).count() == 5
