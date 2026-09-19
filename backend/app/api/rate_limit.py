from __future__ import annotations

from collections import defaultdict, deque
from time import monotonic

from fastapi import HTTPException, Request


class InMemoryRateLimiter:
    def __init__(self, limit: int, window_seconds: int = 60) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._requests: dict[tuple[str, str], deque[float]] = defaultdict(deque)

    def check(self, request: Request, bucket: str) -> None:
        key = (bucket, request.client.host if request.client else "unknown")
        now = monotonic()
        timestamps = self._requests[key]
        while timestamps and now - timestamps[0] >= self.window_seconds:
            timestamps.popleft()
        if len(timestamps) >= self.limit:
            raise HTTPException(status_code=429, detail="Too many requests")
        timestamps.append(now)
        if len(self._requests) > 10000:
            self._requests = {key: value for key, value in self._requests.items() if value and now - value[-1] < self.window_seconds}


interest_analysis_limiter = InMemoryRateLimiter(limit=60)
recommendation_limiter = InMemoryRateLimiter(limit=30)
icebreaker_limiter = InMemoryRateLimiter(limit=30)


def limit_interest_analysis(request: Request) -> None:
    interest_analysis_limiter.check(request, "interest-analysis")


def limit_recommendations(request: Request) -> None:
    recommendation_limiter.check(request, "recommendations")


def limit_icebreakers(request: Request) -> None:
    icebreaker_limiter.check(request, "icebreakers")
