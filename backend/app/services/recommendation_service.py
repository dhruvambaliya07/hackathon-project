from uuid import UUID

from app.services.matching_service import StubMatchingService


class RecommendationService:
    def __init__(self) -> None:
        self.matcher = StubMatchingService()

    async def recommend(self, user_id: UUID | None, interest_text: str, limit: int) -> list[dict[str, object]]:
        return await self.matcher.match(user_id, interest_text, limit)