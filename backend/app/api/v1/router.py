from fastapi import APIRouter

from app.api.v1 import accounts, activities, behavior_templates, campaigns, health, recommendations, upvote

api_router = APIRouter()
api_router.include_router(accounts.router)
api_router.include_router(activities.router)
api_router.include_router(behavior_templates.router)
api_router.include_router(campaigns.router)
api_router.include_router(health.router)
api_router.include_router(recommendations.router)
api_router.include_router(upvote.router)
