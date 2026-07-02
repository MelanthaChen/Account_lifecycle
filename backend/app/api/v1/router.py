from fastapi import APIRouter

from app.api.v1 import accounts, activity, sync

api_router = APIRouter()
api_router.include_router(accounts.router)
api_router.include_router(activity.router)
api_router.include_router(sync.router)
