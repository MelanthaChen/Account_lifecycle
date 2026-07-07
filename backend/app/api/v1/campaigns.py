from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.campaign import CampaignCreate, CampaignRead
from app.schemas.workflow import WorkflowRead, WorkflowRunResponse, WorkflowWrite
from app.services.campaign_service import CampaignService
from app.services.workflow_service import WorkflowService

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


def service(session: AsyncSession = Depends(get_session)) -> CampaignService:
    return CampaignService(session)


def workflow_service(session: AsyncSession = Depends(get_session)) -> WorkflowService:
    return WorkflowService(session)


@router.get("", response_model=list[CampaignRead])
async def list_campaigns(
    campaign_service: CampaignService = Depends(service),
) -> list[CampaignRead]:
    return await campaign_service.list_campaigns()


@router.post("", response_model=CampaignRead, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    payload: CampaignCreate,
    campaign_service: CampaignService = Depends(service),
) -> CampaignRead:
    return await campaign_service.create_campaign(payload)


@router.get("/{campaign_id}", response_model=CampaignRead)
async def get_campaign(
    campaign_id: UUID,
    campaign_service: CampaignService = Depends(service),
) -> CampaignRead:
    return await campaign_service.get_campaign(campaign_id)


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: UUID,
    campaign_service: CampaignService = Depends(service),
) -> Response:
    await campaign_service.delete_campaign(campaign_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{campaign_id}/run", response_model=WorkflowRunResponse)
async def run_campaign(
    campaign_id: UUID,
    campaign_service: CampaignService = Depends(service),
) -> WorkflowRunResponse:
    return await campaign_service.run_campaign(campaign_id)


@router.get("/{campaign_id}/workflow", response_model=WorkflowRead)
async def get_campaign_workflow(
    campaign_id: UUID,
    workflows: WorkflowService = Depends(workflow_service),
) -> WorkflowRead:
    return await workflows.get_workflow(campaign_id)


@router.post("/{campaign_id}/workflow", response_model=WorkflowRead, status_code=status.HTTP_201_CREATED)
async def create_campaign_workflow(
    campaign_id: UUID,
    payload: WorkflowWrite,
    workflows: WorkflowService = Depends(workflow_service),
) -> WorkflowRead:
    return await workflows.create_workflow(campaign_id, payload)


@router.put("/{campaign_id}/workflow", response_model=WorkflowRead)
async def replace_campaign_workflow(
    campaign_id: UUID,
    payload: WorkflowWrite,
    workflows: WorkflowService = Depends(workflow_service),
) -> WorkflowRead:
    return await workflows.replace_workflow(campaign_id, payload)


@router.post("/{campaign_id}/workflow/run", response_model=WorkflowRunResponse)
async def run_campaign_workflow(
    campaign_id: UUID,
    workflows: WorkflowService = Depends(workflow_service),
) -> WorkflowRunResponse:
    return await workflows.run_workflow(campaign_id)
