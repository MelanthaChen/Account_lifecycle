from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.campaign import Campaign, WorkflowStep
from app.models.enums import CampaignActionType, CampaignStatus, WorkflowActionType
from app.repositories.account_repository import AccountRepository
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
from app.services.open_url_service import OpenUrlService
from app.services.upvote_service import UpvoteService


class WorkflowService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.accounts = AccountRepository(session)
        self.campaigns = CampaignRepository(session)
        self.workflows = WorkflowRepository(session)
        self.open_urls = OpenUrlService()
        self.upvotes = UpvoteService(session)

    async def get_workflow(self, campaign_id: UUID) -> WorkflowRead:
        await self._get_campaign(campaign_id)
        steps = await self.workflows.list_steps(campaign_id)
        return WorkflowRead(campaign_id=campaign_id, steps=steps)

    async def create_workflow(self, campaign_id: UUID, payload: WorkflowWrite) -> WorkflowRead:
        return await self.replace_workflow(campaign_id, payload)

    async def replace_workflow(self, campaign_id: UUID, payload: WorkflowWrite) -> WorkflowRead:
        await self._get_campaign(campaign_id)
        self._validate_steps(payload.steps)
        steps = await self.workflows.replace_steps(campaign_id, payload.steps)
        await self.session.commit()
        for step in steps:
            await self.session.refresh(step)
        return WorkflowRead(campaign_id=campaign_id, steps=steps)

    async def run_workflow(self, campaign_id: UUID) -> WorkflowRunResponse:
        campaign = await self._get_campaign(campaign_id)
        account_ids = await self.campaigns.list_account_ids(campaign.id)
        steps = await self.workflows.list_steps(campaign.id)
        if not account_ids:
            raise HTTPException(status.HTTP_409_CONFLICT, "Campaign has no accounts")
        if not steps:
            steps = await self._create_default_workflow(campaign)

        campaign.status = CampaignStatus.RUNNING
        await self.session.commit()
        await self.session.refresh(campaign)

        results: list[WorkflowAccountResult] = []
        for account_id in account_ids:
            account = await self.accounts.get(account_id)
            if account is None:
                results.append(
                    WorkflowAccountResult(
                        account=str(account_id),
                        steps=[WorkflowStepResult(action_type=step.action_type, success=False, reason="account_not_found") for step in steps],
                    )
                )
                continue
            results.append(await self._run_account_workflow(campaign, account, steps))

        success = all(all(step.success for step in account.steps) for account in results)
        campaign.status = CampaignStatus.COMPLETED if success else CampaignStatus.FAILED
        await self.session.commit()
        return WorkflowRunResponse(campaign_id=campaign.id, success=success, results=results)

    async def _run_account_workflow(
        self,
        campaign: Campaign,
        account: Account,
        steps: list[WorkflowStep],
    ) -> WorkflowAccountResult:
        step_results: list[WorkflowStepResult] = []
        for step in steps:
            result = await self._execute_step(campaign, account, step)
            step_results.append(result)
            if not result.success:
                break
        return WorkflowAccountResult(account=account.nickname, steps=step_results)

    async def _execute_step(
        self,
        campaign: Campaign,
        account: Account,
        step: WorkflowStep,
    ) -> WorkflowStepResult:
        target_url = str(step.config.get("target_url") or campaign.target_url)
        if step.action_type == WorkflowActionType.OPEN_URL:
            result = await self.open_urls.open_url(account, target_url)
            return WorkflowStepResult(action_type=step.action_type, success=result.success, reason=result.reason)

        if step.action_type == WorkflowActionType.UPVOTE:
            results = await self.upvotes.open_target_for_accounts(
                account_ids=[account.id],
                target_url=target_url,
            )
            result = results[0]
            return WorkflowStepResult(
                action_type=step.action_type,
                success=result.opened and result.clicked,
                reason=result.reason,
            )

        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Unsupported workflow action: {step.action_type}")

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
    def _validate_steps(steps: list[WorkflowStepInput]) -> None:
        for step in steps:
            if step.action_type not in {WorkflowActionType.OPEN_URL, WorkflowActionType.UPVOTE}:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Unsupported workflow action: {step.action_type}")
