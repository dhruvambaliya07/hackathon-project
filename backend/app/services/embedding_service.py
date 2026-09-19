from typing import Protocol


class EmbeddingService(Protocol):
    async def embed(self, text: str) -> list[float]: ...


class StubEmbeddingService:
    async def embed(self, text: str) -> list[float]:
        return []