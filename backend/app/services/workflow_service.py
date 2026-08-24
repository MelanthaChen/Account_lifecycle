from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campaign import Campaign, WorkflowStep
from app.models.enums import CampaignActionType, WorkflowActionType
from app.core.platforms import supported_workflow_actions
from app.repositories.campaign_repository import CampaignRepository
from app.repositories.workflow_repository import WorkflowRepository
from app.schemas.workflow import (
    WorkflowAccountResult,
    WorkflowRead,
    WorkflowRunResponse,
    WorkflowStepInput,
    WorkflowStepResult,
    WorkflowWrite,
)
from app.services.automation_job_service import AutomationJobService


class WorkflowService:
    """Stores workflow steps and queues campaign execution jobs."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.campaigns = CampaignRepository(session)
        self.workflows = WorkflowRepository(session)
        self.jobs = AutomationJobService(session)

    async def get_workflow(self, campaign_id: UUID) -> WorkflowRead:
        """Return the workflow steps for one campaign."""
        await self._get_campaign(campaign_id)
        steps = await self.workflows.list_steps(campaign_id)
        return WorkflowRead(campaign_id=campaign_id, steps=steps)

    async def create_workflow(self, campaign_id: UUID, payload: WorkflowWrite) -> WorkflowRead:
        """Create workflow steps for a campaign by replacing existing steps."""
        return await self.replace_workflow(campaign_id, payload)

    async def replace_workflow(self, campaign_id: UUID, payload: WorkflowWrite) -> WorkflowRead:
        """Replace all workflow steps for a campaign."""
        campaign = await self._get_campaign(campaign_id)
        self._validate_steps(campaign, payload.steps)
        steps = await self.workflows.replace_steps(campaign_id, payload.steps)
        await self.session.commit()
        for step in steps:
            await self.session.refresh(step)
        return WorkflowRead(campaign_id=campaign_id, steps=steps)

    async def run_workflow(self, campaign_id: UUID) -> WorkflowRunResponse:
        """Queue campaign workflow jobs for execution by an external automation agent."""
        campaign = await self._get_campaign(campaign_id)
        account_ids = await self.campaigns.list_account_ids(campaign.id)
        steps = await self.workflows.list_steps(campaign.id)
        if not account_ids:
            raise HTTPException(status.HTTP_409_CONFLICT, "Campaign has no accounts")
        if not steps:
            steps = await self._create_default_workflow(campaign)

        jobs = await self.jobs.enqueue_campaign(campaign.id)
        results = [
            WorkflowAccountResult(
                account=str(job.account_id),
                steps=[
                    WorkflowStepResult(
                        action_type=step.action_type,
                        success=True,
                        detail=f"Queued job {job.id}",
                    )
                    for step in steps
                ],
            )
            for job in jobs
        ]
        return WorkflowRunResponse(campaign_id=campaign.id, success=True, results=results)

    async def _create_default_workflow(self, campaign: Campaign) -> list[WorkflowStep]:
        if campaign.action_type != CampaignActionType.UPVOTE:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only UPVOTE campaigns are supported")
        steps = await self.workflows.replace_steps(
            campaign.id,
            [
                WorkflowStepInput(
                    action_type=WorkflowActionType.OPEN_URL,
                    config={"target_url": campaign.target_url},
                ),
                WorkflowStepInput(action_type=WorkflowActionType.UPVOTE, config={}),
            ],
        )
        await self.session.commit()
        return steps

    async def _get_campaign(self, campaign_id: UUID) -> Campaign:
        campaign = await self.campaigns.get(campaign_id)
        if campaign is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Campaign not found")
        return campaign

    @staticmethod
    def _validate_steps(campaign: Campaign, steps: list[WorkflowStepInput]) -> None:
        supported_actions = supported_workflow_actions(campaign.platform)
        for step in steps:
            if step.action_type not in supported_actions:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Unsupported workflow action: {step.action_type}")
