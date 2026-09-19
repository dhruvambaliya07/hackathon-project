from collections.abc import Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.session import SessionLocal, get_db
from app.main import app
from app.models import Group, Interest, Recommendation, User, UserInterest
from app.seed import seed_database, stable_id

pytestmark = pytest.mark.skipif(
    not get_settings().database_url.startswith(("postgres://", "postgresql://", "postgresql+")),
    reason="profile and feedback integration tests require PostgreSQL",
)


@pytest.fixture
def profile_client() -> Generator[tuple[TestClient, User, Group], None, None]:
    try:
        with SessionLocal() as session:
            session.scalar(select(Group.id))
            seed_database(session)
            user = session.get(User, stable_id("user", "maya.shah@example.test"))
            group = session.scalar(select(Group).where(Group.name == "Street Lens Collective"))
            assert user is not None and group is not None
            session.add(Recommendation(id=uuid4(), user_id=user.id, target_type="group", target_id=group.id, score=0.8, reason={}))
            session.commit()
    except SQLAlchemyError as exc:
        pytest.skip(f"PostgreSQL schema is unavailable: {exc}")

    def override_db() -> Generator[Session, None, None]:
        with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    try:
        with SessionLocal() as session:
            user = session.get(User, stable_id("user", "maya.shah@example.test"))
            group = session.scalar(select(Group).where(Group.name == "Street Lens Collective"))
            assert user is not None and group is not None
            yield TestClient(app), user, group
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_profile_retrieval_and_update(profile_client) -> None:
    client, user, _group = profile_client
    response = client.get(f"/api/v1/profile/{user.id}")
    assert response.status_code == 200
    assert response.json()["data"]["user"]["name"] == "Maya Shah"
    assert response.json()["data"]["interests"]

    updated = client.put(
        f"/api/v1/profile/{user.id}",
        json={"name": "Maya Updated", "bio": "New bio", "interests": ["Photography", "Writing"], "goals": ["create"]},
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["user"]["name"] == "Maya Updated"
    assert updated.json()["data"]["goals"] == ["create"]
    assert {item["name"] for item in updated.json()["data"]["interests"]} == {"Photography", "Writing"}


def test_invalid_user_is_rejected(profile_client) -> None:
    client, _user, _group = profile_client
    response = client.get(f"/api/v1/profile/{uuid4()}")
    assert response.status_code == 404


def test_feedback_records_state_and_prevents_duplicates(profile_client) -> None:
    client, user, group = profile_client
    with SessionLocal() as session:
        recommendation = session.scalar(select(Recommendation).where(Recommendation.user_id == user.id))
        assert recommendation is not None
        recommendation_id = recommendation.id
        photography = session.scalar(select(Interest).where(Interest.name == "Photography"))
        assert photography is not None
        before = session.scalar(select(UserInterest.weight).where(UserInterest.user_id == user.id, UserInterest.interest_id == photography.id))

    response = client.post("/api/v1/feedback", json={"user_id": str(user.id), "recommendation_id": str(recommendation_id), "feedback_type": "interested"})
    assert response.status_code == 201
    assert response.json()["data"]["accepted"] is True

    duplicate = client.post("/api/v1/feedback", json={"user_id": str(user.id), "recommendation_id": str(recommendation_id), "feedback_type": "interested"})
    assert duplicate.status_code == 409

    with SessionLocal() as session:
        photography = session.scalar(select(Interest).where(Interest.name == "Photography"))
        after = session.scalar(select(UserInterest.weight).where(UserInterest.user_id == user.id, UserInterest.interest_id == photography.id))
        assert before is not None and after is not None
        assert 0 <= after <= 1
        assert after == 1

        session.add(Recommendation(id=uuid4(), user_id=user.id, target_type="group", target_id=group.id, score=0.7, reason={}))
        session.scalar(select(UserInterest).where(UserInterest.user_id == user.id, UserInterest.interest_id == photography.id)).weight = 0.02
        session.commit()
        lower_bound_recommendation = session.scalar(select(Recommendation).order_by(Recommendation.created_at.desc()))
        assert lower_bound_recommendation is not None

    wrong_match = client.post("/api/v1/feedback", json={"user_id": str(user.id), "recommendation_id": str(lower_bound_recommendation.id), "feedback_type": "wrong_match"})
    assert wrong_match.status_code == 201
    with SessionLocal() as session:
        photography = session.scalar(select(Interest).where(Interest.name == "Photography"))
        after_wrong_match = session.scalar(select(UserInterest.weight).where(UserInterest.user_id == user.id, UserInterest.interest_id == photography.id))
        assert after_wrong_match == 0

    profile = client.get(f"/api/v1/profile/{user.id}")
    assert group.id in {item["id"] for item in profile.json()["data"]["saved_groups"]}
