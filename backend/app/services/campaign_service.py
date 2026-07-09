from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campaign import Campaign
from app.models.enums import CampaignActionType, CampaignStatus, WorkflowActionType
from app.providers.manager import provider_manager
from app.repositories.account_repository import AccountRepository
from app.repositories.campaign_repository import CampaignRepository
from app.repositories.workflow_repository import WorkflowRepository
from app.schemas.campaign import CampaignCreate, CampaignRead
from app.schemas.workflow import WorkflowRunResponse, WorkflowStepInput
from app.services.workflow_service import WorkflowService


class CampaignService:
    """Creates, lists, deletes, and runs campaign orchestration records."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.campaigns = CampaignRepository(session)
        self.accounts = AccountRepository(session)
        self.workflows = WorkflowRepository(session)

    async def list_campaigns(self) -> list[CampaignRead]:
        """Return campaigns with their ordered account assignments."""
        campaigns = await self.campaigns.list()
        return [await self._read(campaign) for campaign in campaigns]

    async def get_campaign(self, campaign_id: UUID) -> CampaignRead:
        """Return one campaign with account assignments."""
        return await self._read(await self._get_campaign_model(campaign_id))

    async def create_campaign(self, payload: CampaignCreate) -> CampaignRead:
        """Create an UPVOTE campaign and its default OPEN_URL plus UPVOTE workflow."""
        await self._validate_accounts(payload.account_ids)
        provider = provider_manager.get_provider(payload.platform)
        if payload.action_type != CampaignActionType.UPVOTE:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only UPVOTE campaigns are supported")
        if WorkflowActionType.UPVOTE not in provider.supported_actions():
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "UPVOTE is not supported for this platform")

        campaign = Campaign(
            name=payload.name,
            description=payload.description,
            platform=payload.platform,
            action_type=payload.action_type,
            target_url=str(payload.target_url),
            status=CampaignStatus.READY,
        )
        await self.campaigns.create(campaign)
        await self.campaigns.replace_accounts(campaign.id, payload.account_ids)
        await self.workflows.replace_steps(
            campaign.id,
            [
                WorkflowStepInput(
                    action_type=WorkflowActionType.OPEN_URL,
                    config={"target_url": str(payload.target_url)},
                ),
                WorkflowStepInput(action_type=WorkflowActionType.UPVOTE, config={}),
            ],
        )
        await self.session.commit()
        await self.session.refresh(campaign)
        return await self._read(campaign)

    async def delete_campaign(self, campaign_id: UUID) -> None:
        """Delete a campaign and cascade related account and workflow rows."""
        campaign = await self._get_campaign_model(campaign_id)
        await self.campaigns.delete(campaign)
        await self.session.commit()

    async def run_campaign(self, campaign_id: UUID) -> WorkflowRunResponse:
        """Run a campaign through the WorkflowService."""
        return await WorkflowService(self.session).run_workflow(campaign_id)

    async def _get_campaign_model(self, campaign_id: UUID) -> Campaign:
        campaign = await self.campaigns.get(campaign_id)
        if campaign is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Campaign not found")
        return campaign

    async def _validate_accounts(self, account_ids: list[UUID]) -> None:
        for account_id in account_ids:
            if await self.accounts.get(account_id) is None:
                raise HTTPException(status.HTTP_404_NOT_FOUND, f"Account not found: {account_id}")

    async def _read(self, campaign: Campaign) -> CampaignRead:
        account_ids = await self.campaigns.list_account_ids(campaign.id)
        return CampaignRead(
            id=campaign.id,
            name=campaign.name,
            description=campaign.description,
            platform=campaign.platform,
            action_type=campaign.action_type,
            target_url=campaign.target_url,
            status=campaign.status,
            account_ids=account_ids,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
        )
