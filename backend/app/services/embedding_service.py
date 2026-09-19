from __future__ import annotations

import hashlib
from typing import Protocol

import httpx

from app.config import Settings, get_settings


class EmbeddingError(Exception):
    """Safe embedding service failure."""


class EmbeddingProvider(Protocol):
    async def embed(self, text: str) -> list[float]: ...


class EmbeddingService(Protocol):
    async def generate_embedding(self, text: str) -> list[float]: ...


class OpenAICompatibleEmbeddingProvider:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def embed(self, text: str) -> list[float]:
        headers = {"Authorization": f"Bearer {self.settings.ai_api_key}"}
        payload = {"model": self.settings.embedding_model, "input": text}
        try:
            async with httpx.AsyncClient(timeout=self.settings.embedding_timeout_seconds) as client:
                response = await client.post(self.settings.embedding_api_url, headers=headers, json=payload)
                response.raise_for_status()
                body = response.json()
                vector = body["data"][0]["embedding"]
                if not isinstance(vector, list) or len(vector) != self.settings.embedding_dimension:
                    raise EmbeddingError("Embedding provider returned an unexpected vector dimension")
                return [float(value) for value in vector]
        except EmbeddingError:
            raise
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError, TimeoutError) as exc:
            raise EmbeddingError("Embedding provider request failed") from exc


class DeterministicEmbeddingProvider:
    """Offline deterministic vector provider for tests and local development."""

    def __init__(self, dimension: int = 1536) -> None:
        self.dimension = dimension

    async def embed(self, text: str) -> list[float]:
        return generate_deterministic_embedding(text, self.dimension)


def generate_deterministic_embedding(text: str, dimension: int = 1536) -> list[float]:
    digest = hashlib.sha256(text.strip().lower().encode("utf-8")).digest()
    return [((digest[index % len(digest)] / 255.0) * 2.0) - 1.0 for index in range(dimension)]


class ProviderEmbeddingService:
    def __init__(self, provider: EmbeddingProvider) -> None:
        self.provider = provider

    async def generate_embedding(self, text: str) -> list[float]:
        return await self.provider.embed(text)


class ResilientEmbeddingService:
    def __init__(self, primary: EmbeddingService, fallback: EmbeddingService) -> None:
        self.primary = primary
        self.fallback = fallback

    async def generate_embedding(self, text: str) -> list[float]:
        try:
            return await self.primary.generate_embedding(text)
        except Exception:
            return await self.fallback.generate_embedding(text)


class StubEmbeddingService(ProviderEmbeddingService):
    def __init__(self) -> None:
        super().__init__(DeterministicEmbeddingProvider())