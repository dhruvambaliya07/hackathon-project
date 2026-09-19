from __future__ import annotations

import json
import re
from typing import Any, Protocol

import httpx

from app.config import Settings, get_settings
from app.schemas.interests import AnalyzedInterest, InterestAnalysis

CONTROLLED_INTERESTS = {
    "ai",
    "machine learning",
    "programming",
    "web development",
    "robotics",
    "cybersecurity",
    "photography",
    "filmmaking",
    "graphic design",
    "art",
    "writing",
    "drama",
    "public speaking",
    "debate",
    "volunteering",
    "event management",
    "leadership",
    "travel",
    "fitness",
    "yoga",
    "cooking",
    "music",
    "dance",
    "gaming",
    "entrepreneurship",
    "finance",
    "marketing",
    "film studies",
    "data science",
    "mental wellness",
}

INTEREST_ALIASES = {
    "photo": "photography",
    "photos": "photography",
    "taking photos": "photography",
    "cameras": "photography",
    "camera": "photography",
    "shooting": "photography",
    "making reels": "filmmaking",
    "video": "filmmaking",
    "videos": "filmmaking",
    "film making": "filmmaking",
    "coding": "programming",
    "software": "programming",
    "developer": "programming",
    "developers": "programming",
    "building websites": "web development",
    "websites": "web development",
    "machine learning": "machine learning",
    "ml": "machine learning",
    "infosec": "cybersecurity",
    "cyber security": "cybersecurity",
    "public speaking": "public speaking",
    "entrepreneurial": "entrepreneurship",
}

GOALS = {"meet_people", "learn", "create", "perform", "stay_active", "build_career", "help_community", "relax"}
TRAITS = {"creative", "collaborative", "analytical", "curious", "technical", "social", "entrepreneurial", "active"}


class AIServiceError(Exception):
    """A safe, user-facing AI service failure without provider details."""


class AIProvider(Protocol):
    async def complete(self, prompt: str) -> str: ...


class AIService(Protocol):
    async def generate_icebreaker(self, context: str) -> str: ...


class OpenAICompatibleProvider:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def complete(self, prompt: str) -> str:
        headers = {"Authorization": f"Bearer {self.settings.ai_api_key}"}
        payload = {
            "model": self.settings.ai_model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": "Return only valid JSON. Never invent interests not supported by the text."},
                {"role": "user", "content": prompt},
            ],
        }
        try:
            async with httpx.AsyncClient(timeout=self.settings.ai_timeout_seconds) as client:
                response = await client.post(self.settings.ai_api_url, headers=headers, json=payload)
                response.raise_for_status()
                body = response.json()
                return str(body["choices"][0]["message"]["content"])
        except (httpx.TimeoutException, TimeoutError) as exc:
            raise AIServiceError("AI provider timed out") from exc
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise AIServiceError("AI provider request failed") from exc


class KeywordFallbackAIService:
    async def analyze_interests(self, text: str) -> InterestAnalysis:
        return fallback_analysis(text)

    async def generate_explanation(self, context: str) -> str:
        return "Fallback explanation: recommendations are based on matching normalized keywords."

    async def generate_icebreaker(self, context: str) -> str:
        return "What part of this interest would you most enjoy exploring with others?"


class StructuredAIService:
    def __init__(self, provider: AIProvider, fallback: AIService | None = None) -> None:
        self.provider = provider
        self.fallback = fallback or KeywordFallbackAIService()

    async def analyze_interests(self, text: str) -> InterestAnalysis:
        try:
            raw = await self.provider.complete(build_analysis_prompt(text))
            parsed = parse_analysis(raw, text)
            return parsed.model_copy(update={"source": "ai", "original_text": text})
        except (AIServiceError, httpx.TimeoutException, TimeoutError):
            return await self.fallback.analyze_interests(text)
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            raise AIServiceError("AI provider returned invalid structured output") from exc

    async def generate_explanation(self, context: str) -> str:
        try:
            return await self.provider.complete(f"Generate a concise explanation for these recommendations: {context}")
        except AIServiceError:
            return await self.fallback.generate_explanation(context)

    async def generate_icebreaker(self, context: str) -> str:
        try:
            return await self.provider.complete(f"Generate one friendly icebreaker for this context: {context}")
        except AIServiceError:
            return await self.fallback.generate_icebreaker(context)


class StubAIService(KeywordFallbackAIService):
    """Backward-compatible name for callers that used the original stub."""


def build_analysis_prompt(text: str) -> str:
    vocabulary = ", ".join(sorted(CONTROLLED_INTERESTS))
    return (
        "Analyze the student's text. Identify only explicit or strongly supported interests. "
        "Normalize synonyms to this vocabulary where possible: "
        f"{vocabulary}. Infer only reasonable goals and traits. "
        "Return JSON with interests [{name, confidence}], goals [string], and traits [string]. "
        "Confidence must be between 0 and 1. Allowed goals: "
        f"{', '.join(sorted(GOALS))}. Allowed traits: {', '.join(sorted(TRAITS))}.\n\nText: "
        f"{text}"
    )


def parse_analysis(raw: str | dict[str, Any], original_text: str) -> InterestAnalysis:
    payload: Any = raw
    if isinstance(raw, str):
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            recovered = _recover_json_object(raw)
            if recovered is None:
                raise
            payload = json.loads(recovered)
    if not isinstance(payload, dict):
        raise TypeError("structured AI output must be an object")
    interests = []
    for item in payload.get("interests", []):
        if isinstance(item, str):
            item = {"name": item, "confidence": 0.7}
        if not isinstance(item, dict):
            raise TypeError("interest item must be an object")
        name = normalize_interest(str(item.get("name", "")))
        if name not in CONTROLLED_INTERESTS:
            continue
        interests.append(AnalyzedInterest(name=name, confidence=float(item.get("confidence", 0))))
    goals = [str(value) for value in payload.get("goals", []) if str(value) in GOALS]
    traits = [str(value) for value in payload.get("traits", []) if str(value) in TRAITS]
    return InterestAnalysis(original_text=original_text, interests=interests, goals=goals, traits=traits, source="ai")


def normalize_interest(value: str) -> str:
    normalized = re.sub(r"\s+", " ", value.strip().lower().replace("_", " "))
    return INTEREST_ALIASES.get(normalized, normalized)


def fallback_analysis(text: str) -> InterestAnalysis:
    lowered = text.lower()
    matches: list[AnalyzedInterest] = []
    for interest in sorted(CONTROLLED_INTERESTS):
        terms = [interest, *[alias for alias, canonical in INTEREST_ALIASES.items() if canonical == interest]]
        if any(re.search(rf"\b{re.escape(term)}\b", lowered) for term in terms):
            matches.append(AnalyzedInterest(name=interest, confidence=0.9 if interest in lowered else 0.78))
    names = {item.name for item in matches}
    goals: list[str] = []
    if names & {"programming", "ai", "machine learning", "robotics", "web development", "cybersecurity", "data science"}:
        goals.append("learn")
    if names & {"photography", "filmmaking", "graphic design", "art", "writing", "drama", "music", "dance"}:
        goals.append("create")
    if names & {"public speaking", "debate", "volunteering", "event management", "leadership"}:
        goals.append("meet_people")
    if names & {"entrepreneurship", "finance", "marketing"}:
        goals.append("build_career")
    traits: list[str] = []
    if names & {"photography", "filmmaking", "graphic design", "art", "writing", "drama", "music", "dance"}:
        traits.append("creative")
    if names & {"public speaking", "debate", "volunteering", "event management", "leadership"}:
        traits.append("collaborative")
    if names & {"programming", "ai", "machine learning", "robotics", "web development", "cybersecurity", "data science"}:
        traits.append("technical")
    return InterestAnalysis(original_text=text, interests=matches, goals=goals, traits=traits, source="fallback")


def _recover_json_object(raw: str) -> str | None:
    start = raw.find("{")
    end = raw.rfind("}")
    if start < 0 or end <= start:
        return None
    return raw[start : end + 1]