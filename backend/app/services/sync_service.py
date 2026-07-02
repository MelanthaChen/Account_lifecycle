from datetime import UTC, datetime
from uuid import UUID

import httpx
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.reddit.client import RedditClient
from app.repositories.activity_repository import ActivityRepository
from app.repositories.sync_job_repository import SyncJobRepository
from app.services.account_service import AccountService


class SyncService:
    def __init__(self, session: AsyncSession, reddit_client: RedditClient | None = None) -> None:
        self.session = session
        self.accounts = AccountService(session)
        self.activity = ActivityRepository(session)
        self.jobs = SyncJobRepository(session)
        self.reddit = reddit_client or RedditClient()

    async def sync_account(self, account_id: UUID):
        account = await self.accounts.get_account(account_id)
        if not account.is_active:
            raise HTTPException(status.HTTP_409_CONFLICT, "Cannot sync an inactive account")

        job = await self.jobs.create(account_id)
        await self.jobs.mark_running(job)
        await self.session.commit()

        try:
            items = await self.reddit.fetch_user_overview(account.reddit_username)
            posts, comments = self.reddit.normalize_overview_items(account.id, items)
            await self.activity.upsert_posts(posts)
            await self.activity.upsert_comments(comments)
            await self.activity.rebuild_subreddit_activity(account.id)
            account.last_sync = datetime.now(UTC)
            await self.jobs.mark_succeeded(job)
            await self.session.commit()
            await self.session.refresh(job)
            return job
        except httpx.HTTPStatusError as exc:
            await self.session.rollback()
            error = f"Reddit returned {exc.response.status_code}"
        except Exception as exc:  # noqa: BLE001
            await self.session.rollback()
            error = str(exc)

        await self.jobs.mark_failed(job, error)
        await self.session.commit()
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Sync failed: {error}")

    async def list_jobs(self, account_id: UUID):
        await self.accounts.get_account(account_id)
        return await self.jobs.list_for_account(account_id)
