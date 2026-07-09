from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.activity import Activity
from app.models.enums import ActivityStatus, ActivityType
from app.providers.manager import provider_manager
from app.repositories.account_repository import AccountRepository
from app.repositories.activity_repository import ActivityRepository


class ActivityService:
    """Records and retrieves account operation audit events."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.activities = ActivityRepository(session)
        self.accounts = AccountRepository(session)

    async def list_activities(
        self,
        *,
        account_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
        activity_type: ActivityType | None = None,
        status: ActivityStatus | None = None,
    ) -> list[Activity]:
        """Return activity records with optional account, type, and status filters."""
        return await self.activities.list(
            account_id=account_id,
            limit=limit,
            offset=offset,
            activity_type=activity_type,
            status=status,
        )

    async def get_activity(self, activity_id: UUID) -> Activity:
        """Return one activity record or raise 404 when it does not exist."""
        activity = await self.activities.get(activity_id)
        if activity is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Activity not found")
        return activity

    async def delete_activity(self, activity_id: UUID) -> None:
        """Delete one activity record."""
        activity = await self.get_activity(activity_id)
        await self.activities.delete(activity)
        await self.session.commit()

    async def create_test_activity(self, account_id: UUID | None = None) -> Activity:
        """Create a synthetic browse activity for UI verification."""
        account = await self._get_account_for_activity(account_id)
        provider = provider_manager.get_provider(account.platform)
        return await self.record(
            account=account,
            activity_type=ActivityType.BROWSE,
            status=ActivityStatus.SUCCESS,
            target_url=provider.home_url,
            title="Generated test activity",
            metadata={"source": "test_button"},
        )

    async def record_start(
        self,
        *,
        account: Account,
        activity_type: ActivityType,
        target_url: str | None = None,
        title: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Activity:
        """Create a RUNNING activity record at the beginning of an operation."""
        return await self.record(
            account=account,
            activity_type=activity_type,
            status=ActivityStatus.RUNNING,
            target_url=target_url,
            title=title,
            metadata=metadata,
            started_at=datetime.now(UTC),
        )

    async def record_success(
        self,
        activity: Activity,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> Activity:
        """Mark a RUNNING activity as SUCCESS and calculate duration."""
        activity.status = ActivityStatus.SUCCESS
        activity.finished_at = datetime.now(UTC)
        activity.duration_ms = self._duration_ms(activity)
        if metadata is not None:
            activity.metadata_ = {**(activity.metadata_ or {}), **metadata}
        await self.session.commit()
        await self.session.refresh(activity)
        return activity

    async def record_failure(
        self,
        activity: Activity,
        error: Exception,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> Activity:
        """Mark a RUNNING activity as FAILED and attach the error message."""
        activity.status = ActivityStatus.FAILED
        activity.finished_at = datetime.now(UTC)
        activity.duration_ms = self._duration_ms(activity)
        activity.metadata_ = {
            **(activity.metadata_ or {}),
            **(metadata or {}),
            "error": str(error),
        }
        await self.session.commit()
        await self.session.refresh(activity)
        return activity

    async def record(
        self,
        *,
        account: Account,
        activity_type: ActivityType,
        status: ActivityStatus,
        target_url: str | None = None,
        title: str | None = None,
        metadata: dict[str, Any] | None = None,
        started_at: datetime | None = None,
        finished_at: datetime | None = None,
    ) -> Activity:
        """Create an activity record with an explicit status."""
        started_at = started_at or datetime.now(UTC)
        if status in {ActivityStatus.SUCCESS, ActivityStatus.FAILED, ActivityStatus.CANCELLED}:
            finished_at = finished_at or datetime.now(UTC)
        activity = Activity(
            account_id=account.id,
            platform=account.platform,
            activity_type=activity_type,
            status=status,
            target_url=target_url,
            title=title,
            metadata_=metadata,
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=self._duration_ms_from_values(started_at, finished_at),
        )
        await self.activities.create(activity)
        await self.session.commit()
        await self.session.refresh(activity)
        return activity

    async def _get_account_for_activity(self, account_id: UUID | None) -> Account:
        if account_id is not None:
            account = await self.accounts.get(account_id)
        else:
            accounts = await self.accounts.list()
            account = accounts[0] if accounts else None
        if account is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Account not found")
        return account

    @staticmethod
    def _duration_ms(activity: Activity) -> int | None:
        return ActivityService._duration_ms_from_values(activity.started_at, activity.finished_at)

    @staticmethod
    def _duration_ms_from_values(started_at: datetime | None, finished_at: datetime | None) -> int | None:
        if started_at is None or finished_at is None:
            return None
        return max(0, int((finished_at - started_at).total_seconds() * 1000))
