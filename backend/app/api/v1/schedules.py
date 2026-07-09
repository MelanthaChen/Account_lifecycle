from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.schedule import CampaignScheduleCreate, CampaignScheduleRead, CampaignScheduleUpdate
from app.schemas.workflow import WorkflowRunResponse
from app.services.scheduler_service import SchedulerService

router = APIRouter(tags=["schedules"])


def service(session: AsyncSession = Depends(get_session)) -> SchedulerService:
    return SchedulerService(session)


@router.get("/schedules", response_model=list[CampaignScheduleRead])
async def list_schedules(
    scheduler: SchedulerService = Depends(service),
) -> list[CampaignScheduleRead]:
    return await scheduler.list_schedules()


@router.get("/campaigns/{campaign_id}/schedule", response_model=CampaignScheduleRead)
async def get_campaign_schedule(
    campaign_id: UUID,
    scheduler: SchedulerService = Depends(service),
) -> CampaignScheduleRead:
    return await scheduler.get_for_campaign(campaign_id)


@router.post(
    "/campaigns/{campaign_id}/schedule",
    response_model=CampaignScheduleRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_campaign_schedule(
    campaign_id: UUID,
    payload: CampaignScheduleCreate,
    scheduler: SchedulerService = Depends(service),
) -> CampaignScheduleRead:
    return await scheduler.create_for_campaign(campaign_id, payload)


@router.put("/campaigns/{campaign_id}/schedule", response_model=CampaignScheduleRead)
async def update_campaign_schedule(
    campaign_id: UUID,
    payload: CampaignScheduleUpdate,
    scheduler: SchedulerService = Depends(service),
) -> CampaignScheduleRead:
    return await scheduler.update_for_campaign(campaign_id, payload)


@router.delete("/campaigns/{campaign_id}/schedule", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign_schedule(
    campaign_id: UUID,
    scheduler: SchedulerService = Depends(service),
) -> Response:
    await scheduler.delete_for_campaign(campaign_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/campaigns/{campaign_id}/schedule/run-now", response_model=WorkflowRunResponse)
async def run_campaign_schedule_now(
    campaign_id: UUID,
    scheduler: SchedulerService = Depends(service),
) -> WorkflowRunResponse:
    return await scheduler.run_now(campaign_id)
