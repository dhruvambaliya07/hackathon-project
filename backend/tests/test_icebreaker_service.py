import asyncio
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.v1.icebreakers import get_icebreaker_service
from app.main import app
from app.services.icebreaker_service import IcebreakerService, IcebreakerTargetNotFound


class FakeAIService:
    def __init__(self, response: str | Exception = "AI opener") -> None:
        self.response = response
        self.context = ""

    async def generate_icebreaker(self, context: str) -> str:
        self.context = context
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


class MissingTargetService:
    async def generate(self, user_id, target_type, target_id, style):
        raise IcebreakerTargetNotFound("missing")


def service_for(target_type: str, ai_service: FakeAIService) -> IcebreakerService:
    service = IcebreakerService(SimpleNamespace(), ai_service)
    service._load_user_interests = lambda user_id: {"Photography", "Writing"}  # type: ignore[method-assign]
    target = SimpleNamespace(
        name="Lens Walk",
        category="Creative",
        description="A photo walk for beginners",
        location="Campus garden",
        start_time=SimpleNamespace(isoformat=lambda: "2026-10-01T10:00:00+00:00"),
    )
    service._load_target = lambda requested_type, target_id: (target, {"Photography", "Music"})  # type: ignore[method-assign]
    return service


def test_group_icebreaker_uses_shared_interest_and_context() -> None:
    ai = FakeAIService()
    service = service_for("group", ai)

    result = asyncio.run(service.generate(uuid4(), "group", uuid4(), "casual"))

    assert result == "AI opener"
    assert "Photography" in ai.context
    assert "private user information" in ai.context


def test_event_icebreaker_supports_all_styles() -> None:
    for style in ("casual", "friendly", "professional"):
        ai = FakeAIService()
        service = service_for("event", ai)

        asyncio.run(service.generate(uuid4(), "event", uuid4(), style))

        assert f"Style: {style}" in ai.context
        assert "event name=Lens Walk" in ai.context


def test_missing_target_is_reported() -> None:
    service = IcebreakerService(SimpleNamespace(), FakeAIService())
    service._load_user_interests = lambda user_id: {"Photography"}  # type: ignore[method-assign]
    service._load_target = lambda target_type, target_id: (_ for _ in ()).throw(IcebreakerTargetNotFound("missing"))  # type: ignore[method-assign]

    try:
        asyncio.run(service.generate(uuid4(), "group", uuid4(), "casual"))
    except IcebreakerTargetNotFound:
        pass
    else:
        raise AssertionError("missing target should raise IcebreakerTargetNotFound")


def test_ai_failure_uses_deterministic_shared_interest_fallback() -> None:
    ai = FakeAIService(RuntimeError("provider unavailable"))
    service = service_for("group", ai)

    first = asyncio.run(service.generate(uuid4(), "group", uuid4(), "friendly"))
    second = asyncio.run(service.generate(uuid4(), "group", uuid4(), "friendly"))

    assert first == second == "Hi there! I saw you're interested in Photography too. Are you joining the Lens Walk group?"


def test_invalid_style_is_rejected_without_calling_service() -> None:
    client = TestClient(app)
    app.dependency_overrides[get_icebreaker_service] = lambda: None
    try:
        response = client.post(
            "/api/v1/icebreakers",
            json={"user_id": str(uuid4()), "target_type": "group", "target_id": str(uuid4()), "style": "humorous"},
        )
    finally:
        app.dependency_overrides.pop(get_icebreaker_service, None)

    assert response.status_code == 422


def test_missing_target_returns_not_found() -> None:
    client = TestClient(app)
    app.dependency_overrides[get_icebreaker_service] = MissingTargetService
    try:
        response = client.post(
            "/api/v1/icebreakers",
            json={"user_id": str(uuid4()), "target_type": "event", "target_id": str(uuid4()), "style": "casual"},
        )
    finally:
        app.dependency_overrides.pop(get_icebreaker_service, None)

    assert response.status_code == 404