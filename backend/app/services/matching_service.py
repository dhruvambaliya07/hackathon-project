from typing import Protocol
from uuid import UUID


class MatchingService(Protocol):
    async def match(self, user_id: UUID | None, interest_text: str, limit: int) -> list[dict[str, object]]: ...


class StubMatchingService:
    async def match(self, user_id: UUID | None, interest_text: str, limit: int) -> list[dict[str, object]]:
        return []