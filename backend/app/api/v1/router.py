from fastapi import APIRouter

from app.api.v1 import events, feedback, groups, health, icebreakers, interests, profile, recommendations

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(interests.router, prefix="/interests", tags=["interests"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(groups.router, prefix="/groups", tags=["groups"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(icebreakers.router, prefix="/icebreakers", tags=["icebreakers"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])