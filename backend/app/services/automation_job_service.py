from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.account import Account
from app.models.automation_job import AutomationJob, AutomationWorker
from app.models.campaign import Campaign
from app.models.enums import (
    ActivityStatus,
    ActivityType,
    AutomationJobStatus,
    CampaignStatus,
    WorkflowActionType,
)
from app.repositories.account_repository import AccountRepository
from app.repositories.automation_job_repository import AutomationJobRepository
from app.repositories.campaign_repository import CampaignRepository
from app.repositories.workflow_repository import WorkflowRepository
from app.schemas.account import AccountRead
from app.schemas.automation_job import (
    AutomationJobCreate,
    AutomationJobFail,
    AutomationJobFinish,
    AutomationJobPayload,
    AutomationJobRead,
    AutomationJobStart,
    WorkerHeartbeatSummary,
    WorkerHeartbeatUpdate,
    WorkerRead,
)
from app.schemas.campaign import CampaignRead
from app.services.activity_service import ActivityService


class AutomationJobService:
    """Creates PostgreSQL-backed automation jobs and accepts agent results."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.jobs = AutomationJobRepository(session)
        self.accounts = AccountRepository(session)
        self.campaigns = CampaignRepository(session)
        self.workflows = WorkflowRepository(session)
        self.activities = ActivityService(session)

    async def list_jobs(
        self,
        *,
        limit: int = 50,
        status_filter: AutomationJobStatus | None = None,
    ) -> list[AutomationJob]:
        """Return recent automation jobs."""
        return await self.jobs.list(limit=limit, status=status_filter)

    async def create_job(self, payload: AutomationJobCreate) -> AutomationJob:
        """Create one queued automation job."""
        await self._get_campaign(payload.campaign_id)
        await self._get_account(payload.account_id)
        job = AutomationJob(
            campaign_id=payload.campaign_id,
            account_id=payload.account_id,
            workflow_id=payload.workflow_id,
            status=AutomationJobStatus.QUEUED,
        )
        await self.jobs.create(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def enqueue_campaign(self, campaign_id: UUID) -> list[AutomationJob]:
        """Create one queued job for each account assigned to a campaign."""
        campaign = await self._get_campaign(campaign_id)
        account_ids = await self.campaigns.list_account_ids(campaign_id)
        if not account_ids:
            raise HTTPException(status.HTTP_409_CONFLICT, "Campaign has no accounts")
        steps = await self.workflows.list_steps(campaign_id)
        workflow_id = steps[0].id if steps else None
        jobs: list[AutomationJob] = []
        for account_id in account_ids:
            await self._get_account(account_id)
            jobs.append(
                await self.jobs.create(
                    AutomationJob(
                        campaign_id=campaign_id,
                        account_id=account_id,
                        workflow_id=workflow_id,
                        status=AutomationJobStatus.QUEUED,
                    )
                )
            )
        campaign.status = CampaignStatus.RUNNING
        await self.session.commit()
        for job in jobs:
            await self.session.refresh(job)
        return jobs

    async def next_job(self, *, worker_id: str) -> AutomationJobPayload | None:
        """Return the oldest queued job with all execution payload required by an agent."""
        job = await self.jobs.next_queued()
        if job is None:
            await self._upsert_worker(worker_id, status_value="IDLE", running_job=None)
            await self.session.commit()
            return None
        await self._upsert_worker(worker_id, status_value="IDLE", running_job=None)
        await self.session.commit()
        return await self._payload(job)

    async def start_job(self, job_id: UUID, payload: AutomationJobStart, *, worker_id: str) -> AutomationJob:
        """Mark a queued job as running."""
        job = await self._get_job(job_id)
        if job.status != AutomationJobStatus.QUEUED:
            raise HTTPException(status.HTTP_409_CONFLICT, f"Job is already {job.status}")
        job.status = AutomationJobStatus.RUNNING
        job.started_at = datetime.now(UTC)
        job.worker_id = self._resolve_worker_id(payload.worker_id, worker_id)
        await self._upsert_worker(job.worker_id, status_value="RUNNING", running_job=job.id)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def finish_job(self, job_id: UUID, payload: AutomationJobFinish, *, worker_id: str) -> AutomationJob:
        """Mark a running job as successful and persist the agent result."""
        job = await self._get_job(job_id)
        resolved_worker_id = self._resolve_worker_id(payload.worker_id, worker_id)
        self._assert_worker_owns_job(job, resolved_worker_id)
        if job.status != AutomationJobStatus.RUNNING:
            raise HTTPException(status.HTTP_409_CONFLICT, f"Job is {job.status}")
        job.status = AutomationJobStatus.SUCCESS
        job.completed_at = datetime.now(UTC)
        job.worker_id = resolved_worker_id
        job.result_json = payload.result_json
        job.error = None
        await self._record_result_activities(job, payload.result_json, ActivityStatus.SUCCESS)
        await self._update_campaign_status(job.campaign_id)
        await self._upsert_worker(resolved_worker_id, status_value="IDLE", running_job=None)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def fail_job(self, job_id: UUID, payload: AutomationJobFail, *, worker_id: str) -> AutomationJob:
        """Mark a running job as failed and persist the error returned by the agent."""
        job = await self._get_job(job_id)
        resolved_worker_id = self._resolve_worker_id(payload.worker_id, worker_id)
        self._assert_worker_owns_job(job, resolved_worker_id)
        if job.status != AutomationJobStatus.RUNNING:
            raise HTTPException(status.HTTP_409_CONFLICT, f"Job is {job.status}")
        job.status = AutomationJobStatus.FAILED
        job.completed_at = datetime.now(UTC)
        job.worker_id = resolved_worker_id
        job.result_json = payload.result_json
        job.error = payload.error
        await self._record_result_activities(job, payload.result_json or {"error": payload.error}, ActivityStatus.FAILED)
        await self._update_campaign_status(job.campaign_id)
        await self._upsert_worker(resolved_worker_id, status_value="IDLE", running_job=None)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def record_heartbeat(self, worker_id: str, payload: WorkerHeartbeatUpdate) -> WorkerHeartbeatSummary:
        """Persist a worker heartbeat and return dashboard-safe worker summary."""
        await self._upsert_worker(
            worker_id,
            hostname=payload.hostname,
            status_value=payload.status,
            running_job=payload.running_job,
        )
        await self.session.commit()
        return await self.heartbeat()

    async def heartbeat(self) -> WorkerHeartbeatSummary:
        """Return queue and active worker counts for dashboard status."""
        workers = [self._worker_read(worker) for worker in await self.jobs.list_workers()]
        return WorkerHeartbeatSummary(
            active_workers=sum(1 for worker in workers if worker.online_status == "Online"),
            workers=workers,
            queued_jobs=await self.jobs.count(AutomationJobStatus.QUEUED),
            running_jobs=await self.jobs.count(AutomationJobStatus.RUNNING),
        )

    async def _payload(self, job: AutomationJob) -> AutomationJobPayload:
        campaign = await self._get_campaign(job.campaign_id)
        account = await self._get_account(job.account_id)
        steps = await self.workflows.list_steps(job.campaign_id)
        return AutomationJobPayload(
            **AutomationJobRead.model_validate(job).model_dump(),
            campaign=await self._campaign_read(campaign),
            account=AccountRead.model_validate(account),
            workflow_steps=steps,
        )

    async def _record_result_activities(
        self,
        job: AutomationJob,
        result: dict[str, Any],
        fallback_status: ActivityStatus,
    ) -> None:
        account = await self._get_account(job.account_id)
        steps = result.get("steps") if isinstance(result, dict) else None
        if not isinstance(steps, list):
            return
        for step in steps:
            if not isinstance(step, dict):
                continue
            activity_type = self._activity_type(str(step.get("action_type") or ""))
            if activity_type is None:
                continue
            success = bool(step.get("success"))
            await self.activities.record(
                account=account,
                activity_type=activity_type,
                status=ActivityStatus.SUCCESS if success else fallback_status,
                target_url=result.get("target_url"),
                title=f"Agent {activity_type.value}",
                metadata={
                    "automation_job_id": str(job.id),
                    "campaign_id": str(job.campaign_id),
                    "worker_id": job.worker_id,
                    "step": step,
                },
                started_at=job.started_at,
                finished_at=job.completed_at,
            )

    async def _update_campaign_status(self, campaign_id: UUID) -> None:
        campaign = await self._get_campaign(campaign_id)
        remaining_query = (
            select(func.count())
            .select_from(AutomationJob)
            .where(AutomationJob.campaign_id == campaign_id)
            .where(AutomationJob.status.in_([AutomationJobStatus.QUEUED, AutomationJobStatus.RUNNING]))
        )
        failed_query = (
            select(func.count())
            .select_from(AutomationJob)
            .where(AutomationJob.campaign_id == campaign_id)
            .where(AutomationJob.status == AutomationJobStatus.FAILED)
        )
        remaining = int(await self.session.scalar(remaining_query) or 0)
        failed = int(await self.session.scalar(failed_query) or 0)
        if remaining:
            campaign.status = CampaignStatus.RUNNING
        else:
            campaign.status = CampaignStatus.FAILED if failed else CampaignStatus.COMPLETED

    async def _campaign_read(self, campaign: Campaign) -> CampaignRead:
        return CampaignRead(
            id=campaign.id,
            name=campaign.name,
            description=campaign.description,
            platform=campaign.platform,
            action_type=campaign.action_type,
            target_url=campaign.target_url,
            comment_text=campaign.comment_text,
            status=campaign.status,
            account_ids=await self.campaigns.list_account_ids(campaign.id),
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
        )

    async def _get_job(self, job_id: UUID) -> AutomationJob:
        job = await self.jobs.get(job_id)
        if job is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Automation job not found")
        return job

    async def _get_campaign(self, campaign_id: UUID) -> Campaign:
        campaign = await self.campaigns.get(campaign_id)
        if campaign is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Campaign not found")
        return campaign

    async def _get_account(self, account_id: UUID) -> Account:
        account = await self.accounts.get(account_id)
        if account is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Account not found")
        return account

    async def _upsert_worker(
        self,
        worker_id: str,
        *,
        hostname: str | None = None,
        status_value: str,
        running_job: UUID | None,
    ) -> AutomationWorker:
        worker = await self.jobs.get_worker(worker_id)
        now = datetime.now(UTC)
        if worker is None:
            worker = AutomationWorker(
                worker_id=worker_id,
                hostname=hostname,
                last_seen=now,
                status=status_value,
                running_job=running_job,
            )
        else:
            worker.hostname = hostname or worker.hostname
            worker.last_seen = now
            worker.status = status_value
            worker.running_job = running_job
        await self.jobs.save_worker(worker)
        return worker

    @staticmethod
    def _resolve_worker_id(payload_worker_id: str | None, authenticated_worker_id: str) -> str:
        if payload_worker_id is not None and payload_worker_id != authenticated_worker_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Worker id does not match credentials")
        return authenticated_worker_id

    @staticmethod
    def _assert_worker_owns_job(job: AutomationJob, worker_id: str) -> None:
        if job.worker_id is not None and job.worker_id != worker_id:
            raise HTTPException(status.HTTP_409_CONFLICT, "Job is owned by another worker")

    @staticmethod
    def _worker_read(worker: AutomationWorker) -> WorkerRead:
        offline_after = get_settings().worker_offline_seconds
        online = (datetime.now(UTC) - worker.last_seen).total_seconds() <= offline_after
        online_status = "Online" if online else "Offline"
        runtime_status = "Running" if online and worker.status.upper() == "RUNNING" else "Idle"
        return WorkerRead(
            worker_id=worker.worker_id,
            hostname=worker.hostname,
            last_seen=worker.last_seen,
            status=runtime_status if online else "Offline",
            online_status=online_status,
            running_job=worker.running_job,
        )

    @staticmethod
    def _activity_type(action_type: str) -> ActivityType | None:
        if action_type == WorkflowActionType.UPVOTE.value:
            return ActivityType.UPVOTE
        if action_type == WorkflowActionType.COMMENT.value:
            return ActivityType.COMMENT
        return None
