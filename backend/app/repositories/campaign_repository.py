from __future__ import annotations

from uuid import UUID

from sqlalchemy import Select, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campaign import Campaign, CampaignAccount


class CampaignRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(self) -> list[Campaign]:
        query: Select[tuple[Campaign]] = select(Campaign).order_by(Campaign.updated_at.desc())
        return list((await self.session.scalars(query)).all())

    async def get(self, campaign_id: UUID) -> Campaign | None:
        return await self.session.get(Campaign, campaign_id)

    async def create(self, campaign: Campaign) -> Campaign:
        self.session.add(campaign)
        await self.session.flush()
        return campaign

    async def delete(self, campaign: Campaign) -> None:
        await self.session.delete(campaign)

    async def replace_accounts(self, campaign_id: UUID, account_ids: list[UUID]) -> None:
        await self.session.execute(delete(CampaignAccount).where(CampaignAccount.campaign_id == campaign_id))
        for index, account_id in enumerate(account_ids):
            self.session.add(
                CampaignAccount(
                    campaign_id=campaign_id,
                    account_id=account_id,
                    execution_order=index,
                )
            )
        await self.session.flush()

    async def list_account_ids(self, campaign_id: UUID) -> list[UUID]:
        query = (
            select(CampaignAccount.account_id)
            .where(CampaignAccount.campaign_id == campaign_id)
            .order_by(CampaignAccount.execution_order.asc())
        )
        return list((await self.session.scalars(query)).all())
