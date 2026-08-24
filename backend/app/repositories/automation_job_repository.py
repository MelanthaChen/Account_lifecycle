from __future__ import annotations

from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.automation_job import AutomationJob, AutomationWorker
from app.models.enums import AutomationJobStatus


class AutomationJobRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, job: AutomationJob) -> AutomationJob:
        self.session.add(job)
        await self.session.flush()
        return job

    async def get(self, job_id: UUID) -> AutomationJob | None:
        return await self.session.get(AutomationJob, job_id)

    async def list(self, *, limit: int = 50, status: AutomationJobStatus | None = None) -> list[AutomationJob]:
        query: Select[tuple[AutomationJob]] = select(AutomationJob).order_by(AutomationJob.queued_at.desc()).limit(limit)
        if status is not None:
            query = query.where(AutomationJob.status == status)
        return list((await self.session.scalars(query)).all())

    async def next_queued(self) -> AutomationJob | None:
        query = (
            select(AutomationJob)
            .where(AutomationJob.status == AutomationJobStatus.QUEUED)
            .order_by(AutomationJob.queued_at.asc())
            .limit(1)
        )
        return await self.session.scalar(query)

    async def count(self, status: AutomationJobStatus) -> int:
        query = select(func.count()).select_from(AutomationJob).where(AutomationJob.status == status)
        return int(await self.session.scalar(query) or 0)

    async def active_workers(self) -> list[str]:
        query = (
            select(AutomationJob.worker_id)
            .where(AutomationJob.status == AutomationJobStatus.RUNNING)
            .where(AutomationJob.worker_id.is_not(None))
            .distinct()
        )
        return [worker for worker in (await self.session.scalars(query)).all() if worker]

    async def list_workers(self) -> list[AutomationWorker]:
        query = select(AutomationWorker).order_by(AutomationWorker.last_seen.desc())
        return list((await self.session.scalars(query)).all())

    async def get_worker(self, worker_id: str) -> AutomationWorker | None:
        return await self.session.get(AutomationWorker, worker_id)

    async def save_worker(self, worker: AutomationWorker) -> AutomationWorker:
        self.session.add(worker)
        await self.session.flush()
        return worker
