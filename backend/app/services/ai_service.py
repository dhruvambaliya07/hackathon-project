from typing import Protocol


class AIService(Protocol):
    async def analyze_interests(self, text: str) -> list[str]: ...


class StubAIService:
    async def analyze_interests(self, text: str) -> list[str]:
        return []