from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.activity import CommentRead, PostRead
from app.services.activity_service import ActivityService

router = APIRouter(prefix="/accounts/{account_id}/activity", tags=["activity"])


def service(session: AsyncSession = Depends(get_session)) -> ActivityService:
    return ActivityService(session)


@router.get("/posts", response_model=list[PostRead])
async def list_posts(
    account_id: UUID,
    limit: int = Query(default=50, ge=1, le=200),
    activity_service: ActivityService = Depends(service),
) -> list[PostRead]:
    return await activity_service.list_posts(account_id, limit)


@router.get("/comments", response_model=list[CommentRead])
async def list_comments(
    account_id: UUID,
    limit: int = Query(default=50, ge=1, le=200),
    activity_service: ActivityService = Depends(service),
) -> list[CommentRead]:
    return await activity_service.list_comments(account_id, limit)
