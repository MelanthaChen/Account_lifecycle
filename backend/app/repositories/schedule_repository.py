from __future__ import annotations

from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campaign import CampaignSchedule


class ScheduleRepository:
    """Persists campaign schedule records."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(self) -> list[CampaignSchedule]:
        query: Select[tuple[CampaignSchedule]] = select(CampaignSchedule).order_by(
            CampaignSchedule.next_run_at.asc().nulls_last(),
            CampaignSchedule.updated_at.desc(),
        )
        return list((await self.session.scalars(query)).all())

    async def list_enabled(self) -> list[CampaignSchedule]:
        query = select(CampaignSchedule).where(CampaignSchedule.enabled.is_(True))
        return list((await self.session.scalars(query)).all())

    async def get(self, schedule_id: UUID) -> CampaignSchedule | None:
        return await self.session.get(CampaignSchedule, schedule_id)

    async def get_by_campaign(self, campaign_id: UUID) -> CampaignSchedule | None:
        query = select(CampaignSchedule).where(CampaignSchedule.campaign_id == campaign_id)
        return await self.session.scalar(query)

    async def save(self, schedule: CampaignSchedule) -> CampaignSchedule:
        self.session.add(schedule)
        await self.session.flush()
        return schedule

    async def delete(self, schedule: CampaignSchedule) -> None:
        await self.session.delete(schedule)
