from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.enums import ActivityStatus, ActivityType
from app.schemas.activity import ActivityRead
from app.services.activity_service import ActivityService

router = APIRouter(tags=["activities"])


def service(session: AsyncSession = Depends(get_session)) -> ActivityService:
    return ActivityService(session)


@router.get("/activities", response_model=list[ActivityRead])
async def list_activities(
    limit: int = 50,
    offset: int = 0,
    activity_type: ActivityType | None = None,
    status: ActivityStatus | None = None,
    activity_service: ActivityService = Depends(service),
) -> list[ActivityRead]:
    return await activity_service.list_activities(
        limit=limit,
        offset=offset,
        activity_type=activity_type,
        status=status,
    )


@router.get("/accounts/{account_id}/activities", response_model=list[ActivityRead])
async def list_account_activities(
    account_id: UUID,
    limit: int = 50,
    offset: int = 0,
    activity_type: ActivityType | None = None,
    status: ActivityStatus | None = None,
    activity_service: ActivityService = Depends(service),
) -> list[ActivityRead]:
    return await activity_service.list_activities(
        account_id=account_id,
        limit=limit,
        offset=offset,
        activity_type=activity_type,
        status=status,
    )


@router.get("/activities/{activity_id}", response_model=ActivityRead)
async def get_activity(
    activity_id: UUID,
    activity_service: ActivityService = Depends(service),
) -> ActivityRead:
    return await activity_service.get_activity(activity_id)


@router.delete("/activities/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    activity_id: UUID,
    activity_service: ActivityService = Depends(service),
) -> Response:
    await activity_service.delete_activity(activity_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/accounts/{account_id}/activities/test", response_model=ActivityRead, status_code=status.HTTP_201_CREATED)
async def create_account_test_activity(
    account_id: UUID,
    activity_service: ActivityService = Depends(service),
) -> ActivityRead:
    return await activity_service.create_test_activity(account_id)


@router.post("/activities/test", response_model=ActivityRead, status_code=status.HTTP_201_CREATED)
async def create_test_activity(
    activity_service: ActivityService = Depends(service),
) -> ActivityRead:
    return await activity_service.create_test_activity()
