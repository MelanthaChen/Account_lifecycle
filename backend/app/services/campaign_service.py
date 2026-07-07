from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campaign import Campaign
from app.models.enums import CampaignActionType, CampaignStatus
from app.repositories.account_repository import AccountRepository
from app.repositories.campaign_repository import CampaignRepository
from app.schemas.campaign import CampaignCreate, CampaignRead, CampaignRunResponse, CampaignRunResult
from app.services.upvote_service import UpvoteService, UpvoteExecutionResult


class CampaignService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.campaigns = CampaignRepository(session)
        self.accounts = AccountRepository(session)
        self.upvotes = UpvoteService(session)

    async def list_campaigns(self) -> list[CampaignRead]:
        campaigns = await self.campaigns.list()
        return [await self._read(campaign) for campaign in campaigns]

    async def get_campaign(self, campaign_id: UUID) -> CampaignRead:
        return await self._read(await self._get_campaign_model(campaign_id))

    async def create_campaign(self, payload: CampaignCreate) -> CampaignRead:
        await self._validate_accounts(payload.account_ids)
        if payload.action_type != CampaignActionType.UPVOTE:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only UPVOTE campaigns are supported")

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
        await self.session.commit()
        await self.session.refresh(campaign)
        return await self._read(campaign)

    async def delete_campaign(self, campaign_id: UUID) -> None:
        campaign = await self._get_campaign_model(campaign_id)
        await self.campaigns.delete(campaign)
        await self.session.commit()

    async def run_campaign(self, campaign_id: UUID) -> CampaignRunResponse:
        campaign = await self._get_campaign_model(campaign_id)
        account_ids = await self.campaigns.list_account_ids(campaign.id)
        if campaign.action_type != CampaignActionType.UPVOTE:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only UPVOTE campaigns are supported")
        if not account_ids:
            raise HTTPException(status.HTTP_409_CONFLICT, "Campaign has no accounts")

        campaign.status = CampaignStatus.RUNNING
        await self.session.commit()
        await self.session.refresh(campaign)

        results = await self.upvotes.open_target_for_accounts(
            account_ids=account_ids,
            target_url=campaign.target_url,
        )
        campaign.status = CampaignStatus.COMPLETED if all(result.reason is None for result in results) else CampaignStatus.FAILED
        await self.session.commit()
        await self.session.refresh(campaign)

        return CampaignRunResponse(
            campaign=await self._read(campaign),
            success=campaign.status == CampaignStatus.COMPLETED,
            results=[self._serialize_result(result) for result in results],
        )

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

    @staticmethod
    def _serialize_result(result: UpvoteExecutionResult) -> CampaignRunResult:
        return CampaignRunResult(
            account=result.account,
            opened=result.opened,
            clicked=result.clicked,
            verified=result.verified,
            reason=result.reason,
        )
