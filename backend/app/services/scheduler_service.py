from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any
from uuid import UUID
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory
from app.models.campaign import CampaignSchedule
from app.models.enums import ActivityStatus, ActivityType, ScheduleType
from app.repositories.account_repository import AccountRepository
from app.repositories.campaign_repository import CampaignRepository
from app.repositories.schedule_repository import ScheduleRepository
from app.schemas.schedule import CampaignScheduleCreate, CampaignScheduleUpdate
from app.services.activity_service import ActivityService
from app.services.campaign_service import CampaignService


class SchedulerRuntime:
    """Owns APScheduler lifecycle and campaign job registration."""

    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler(timezone="UTC")

    async def start(self) -> None:
        """Start APScheduler and register enabled schedules from the database."""
        if not self.scheduler.running:
            self.scheduler.start()
        await self.reload_jobs()

    async def shutdown(self) -> None:
        """Stop APScheduler gracefully."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    async def reload_jobs(self) -> None:
        """Replace scheduler jobs with the enabled schedules stored in the database."""
        self.scheduler.remove_all_jobs()
        async with async_session_factory() as session:
            schedules = await ScheduleRepository(session).list_enabled()
            for schedule in schedules:
                await self.register_schedule(schedule, session=session)

    async def register_schedule(
        self,
        schedule: CampaignSchedule,
        *,
        session: AsyncSession | None = None,
    ) -> None:
        """Register or replace one APScheduler job for an enabled schedule."""
        self.remove_schedule(schedule.id)
        if not schedule.enabled:
            return

        trigger = self._trigger_for(schedule)
        job = self.scheduler.add_job(
            self.run_schedule,
            trigger=trigger,
            id=self._job_id(schedule.id),
            args=[schedule.id],
            replace_existing=True,
            coalesce=True,
            max_instances=1,
            misfire_grace_time=300,
        )
        next_run_at = getattr(job, "next_run_time", None)
        if next_run_at is not None:
            schedule.next_run_at = next_run_at
            if session is not None:
                await session.commit()

    def remove_schedule(self, schedule_id: UUID) -> None:
        """Remove one registered APScheduler job when it exists."""
        job_id = self._job_id(schedule_id)
        if self.scheduler.get_job(job_id) is not None:
            self.scheduler.remove_job(job_id)

    async def run_schedule(self, schedule_id: UUID) -> None:
        """Execute a schedule job and update its stored run metadata."""
        async with async_session_factory() as session:
            await SchedulerService(session, runtime=self).execute_schedule(schedule_id)

    @staticmethod
    def _job_id(schedule_id: UUID) -> str:
        return f"campaign-schedule:{schedule_id}"

    @staticmethod
    def _trigger_for(schedule: CampaignSchedule) -> DateTrigger | CronTrigger:
        timezone = ZoneInfo(schedule.timezone)
        if schedule.schedule_type == ScheduleType.ONCE:
            if schedule.next_run_at is None:
                raise ValueError("ONCE schedules require next_run_at")
            return DateTrigger(run_date=schedule.next_run_at, timezone=timezone)

        if not schedule.cron_expression:
            raise ValueError("Recurring schedules require cron_expression")
        return CronTrigger.from_crontab(schedule.cron_expression, timezone=timezone)


class SchedulerService:
    """Coordinates schedule CRUD and delegates execution to CampaignService."""

    def __init__(self, session: AsyncSession, *, runtime: SchedulerRuntime | None = None) -> None:
        self.session = session
        self.runtime = runtime or scheduler_runtime
        self.schedules = ScheduleRepository(session)
        self.campaigns = CampaignRepository(session)

    async def list_schedules(self) -> list[CampaignSchedule]:
        """Return all campaign schedules."""
        return await self.schedules.list()

    async def get_for_campaign(self, campaign_id: UUID) -> CampaignSchedule:
        """Return one campaign schedule or raise 404."""
        schedule = await self.schedules.get_by_campaign(campaign_id)
        if schedule is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Schedule not found")
        return schedule

    async def create_for_campaign(
        self,
        campaign_id: UUID,
        payload: CampaignScheduleCreate,
    ) -> CampaignSchedule:
        """Create a schedule for a campaign and register its job when enabled."""
        await self._get_campaign(campaign_id)
        existing = await self.schedules.get_by_campaign(campaign_id)
        if existing is not None:
            raise HTTPException(status.HTTP_409_CONFLICT, "Campaign schedule already exists")
        schedule = CampaignSchedule(campaign_id=campaign_id, **payload.model_dump())
        await self._validate_schedule(schedule)
        await self.schedules.save(schedule)
        await self.session.commit()
        await self.session.refresh(schedule)
        await self.runtime.register_schedule(schedule, session=self.session)
        await self.session.refresh(schedule)
        return schedule

    async def update_for_campaign(
        self,
        campaign_id: UUID,
        payload: CampaignScheduleUpdate,
    ) -> CampaignSchedule:
        """Replace a campaign schedule and refresh its registered job."""
        schedule = await self.get_for_campaign(campaign_id)
        for key, value in payload.model_dump().items():
            setattr(schedule, key, value)
        await self._validate_schedule(schedule)
        await self.session.commit()
        await self.session.refresh(schedule)
        await self.runtime.register_schedule(schedule, session=self.session)
        await self.session.refresh(schedule)
        return schedule

    async def delete_for_campaign(self, campaign_id: UUID) -> None:
        """Delete a campaign schedule and unregister its job."""
        schedule = await self.get_for_campaign(campaign_id)
        self.runtime.remove_schedule(schedule.id)
        await self.schedules.delete(schedule)
        await self.session.commit()

    async def run_now(self, campaign_id: UUID) -> dict[str, Any]:
        """Immediately execute the campaign through the scheduler execution path."""
        schedule = await self.get_for_campaign(campaign_id)
        return await self.execute_schedule(schedule.id)

    async def execute_schedule(self, schedule_id: UUID) -> dict[str, Any]:
        """Run one stored schedule by invoking CampaignService.run()."""
        schedule = await self.schedules.get(schedule_id)
        if schedule is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Schedule not found")

        started_at = datetime.now(UTC)
        try:
            result = await CampaignService(self.session).run(schedule.campaign_id)
            schedule.last_status = "SUCCESS" if result.success else "FAILED"
            return_value = result.model_dump(mode="json")
            await self._record_scheduled_activities(schedule, return_value, started_at)
        except Exception:
            schedule.last_status = "FAILED"
            schedule.last_run_at = datetime.now(UTC)
            await self.session.commit()
            raise

        schedule.last_run_at = datetime.now(UTC)
        if schedule.schedule_type == ScheduleType.ONCE:
            schedule.enabled = False
            self.runtime.remove_schedule(schedule.id)
        else:
            await self.runtime.register_schedule(schedule, session=self.session)
        await self.session.commit()
        await self.session.refresh(schedule)
        return return_value

    async def _record_scheduled_activities(
        self,
        schedule: CampaignSchedule,
        result: dict[str, Any],
        started_at: datetime,
    ) -> None:
        account_ids = await self.campaigns.list_account_ids(schedule.campaign_id)
        accounts = AccountRepository(self.session)
        activity_service = ActivityService(self.session)
        success = bool(result.get("success"))
        for account_id in account_ids:
            account = await accounts.get(account_id)
            if account is None:
                continue
            await activity_service.record(
                account=account,
                activity_type=ActivityType.BROWSE,
                status=ActivityStatus.SUCCESS if success else ActivityStatus.FAILED,
                title="Scheduled campaign run",
                metadata={
                    "campaign_id": str(schedule.campaign_id),
                    "schedule_id": str(schedule.id),
                    "source": "scheduler",
                },
                started_at=started_at,
                finished_at=datetime.now(UTC),
            )

    async def _get_campaign(self, campaign_id: UUID):
        campaign = await self.campaigns.get(campaign_id)
        if campaign is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Campaign not found")
        return campaign

    @staticmethod
    async def _validate_schedule(schedule: CampaignSchedule) -> None:
        try:
            SchedulerRuntime._trigger_for(schedule)
        except Exception as exc:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc


scheduler_runtime = SchedulerRuntime()


@asynccontextmanager
async def scheduler_lifespan(_: object) -> AsyncIterator[None]:
    """Start and stop the campaign scheduler around FastAPI lifespan."""
    await scheduler_runtime.start()
    try:
        yield
    finally:
        await scheduler_runtime.shutdown()
