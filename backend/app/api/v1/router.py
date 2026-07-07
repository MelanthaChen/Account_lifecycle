from fastapi import APIRouter

from app.api.v1 import accounts, activities, campaigns, upvote

api_router = APIRouter()
api_router.include_router(accounts.router)
api_router.include_router(activities.router)
api_router.include_router(campaigns.router)
api_router.include_router(upvote.router)
