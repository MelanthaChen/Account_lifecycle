from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.automation_job import AutomationJob
from app.services.automation_job_service import AutomationJobService


class CommentService:
    """Queues standalone comment jobs for execution by the automation agent."""

    def __init__(self, session: AsyncSession) -> None:
        self.jobs = AutomationJobService(session)

    async def enqueue(
        self,
        *,
        account_ids: list[UUID],
        target_url: str,
        comment_text: str,
    ) -> list[AutomationJob]:
        """Create one queued comment job per selected account."""
        return await self.jobs.enqueue_comment(
            account_ids=account_ids,
            target_url=target_url,
            comment_text=comment_text,
        )
