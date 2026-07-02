from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import SyncJobStatus
from app.models.sync_job import SyncJob


class SyncJobRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, account_id: UUID) -> SyncJob:
        job = SyncJob(account_id=account_id, status=SyncJobStatus.QUEUED)
        self.session.add(job)
        await self.session.flush()
        return job

    async def list_for_account(self, account_id: UUID, limit: int = 25) -> list[SyncJob]:
        query = (
            select(SyncJob)
            .where(SyncJob.account_id == account_id)
            .order_by(desc(SyncJob.created_at))
            .limit(limit)
        )
        return list((await self.session.scalars(query)).all())

    async def mark_running(self, job: SyncJob) -> SyncJob:
        job.status = SyncJobStatus.RUNNING
        job.started_at = datetime.now(UTC)
        await self.session.flush()
        return job

    async def mark_succeeded(self, job: SyncJob) -> SyncJob:
        job.status = SyncJobStatus.SUCCEEDED
        job.finished_at = datetime.now(UTC)
        await self.session.flush()
        return job

    async def mark_failed(self, job: SyncJob, error: str) -> SyncJob:
        job.status = SyncJobStatus.FAILED
        job.error = error
        job.finished_at = datetime.now(UTC)
        await self.session.flush()
        return job
