from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.enums import ActivityType
from app.repositories.account_repository import AccountRepository
from app.services.activity_service import ActivityService
from app.services.browser_manager import browser_manager
from app.services.browser_sessions.base import BrowserSessionResult


class BrowserSessionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.accounts = AccountRepository(session)
        self.browser_manager = browser_manager
        self.activity_service = ActivityService(session)

    async def create(self, account_id: UUID) -> Account:
        account = await self._get_account(account_id)
        activity = await self.activity_service.record_start(
            account=account,
            activity_type=ActivityType.LOGIN,
            target_url="https://www.reddit.com/login/",
            title="Create browser session",
        )
        try:
            result = await self.browser_manager.create_session(account)
        except NotImplementedError as exc:
            await self.activity_service.record_failure(activity, exc)
            raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, str(exc)) from exc
        except Exception as exc:
            await self.activity_service.record_failure(activity, exc)
            raise
        await self.activity_service.record_success(activity)
        return await self._apply_result(account, result)

    async def finish(self, account_id: UUID) -> Account:
        account = await self._get_account(account_id)
        activity = await self.activity_service.record_start(
            account=account,
            activity_type=ActivityType.LOGIN,
            target_url="https://www.reddit.com/login/",
            title="Finish browser session",
        )
        try:
            result = await self.browser_manager.finish_session(account)
        except NotImplementedError as exc:
            await self.activity_service.record_failure(activity, exc)
            raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, str(exc)) from exc
        except Exception as exc:
            await self.activity_service.record_failure(activity, exc)
            raise
        await self.activity_service.record_success(activity, metadata={"session_status": result.session_status})
        return await self._apply_result(account, result)

    async def validate(self, account_id: UUID) -> Account:
        account = await self._get_account(account_id)
        activity = await self.activity_service.record_start(
            account=account,
            activity_type=ActivityType.VALIDATE_SESSION,
            title="Validate browser session",
        )
        try:
            result = await self.browser_manager.validate_session(account)
        except NotImplementedError as exc:
            await self.activity_service.record_failure(activity, exc)
            raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, str(exc)) from exc
        except Exception as exc:
            await self.activity_service.record_failure(activity, exc)
            raise
        await self.activity_service.record_success(activity, metadata={"session_status": result.session_status})
        return await self._apply_result(account, result)

    async def refresh(self, account_id: UUID) -> Account:
        account = await self._get_account(account_id)
        activity = await self.activity_service.record_start(
            account=account,
            activity_type=ActivityType.REFRESH_SESSION,
            title="Refresh browser session",
        )
        try:
            result = await self.browser_manager.refresh_session(account)
        except Exception as exc:
            await self.activity_service.record_failure(activity, exc)
            raise
        await self.activity_service.record_success(activity, metadata={"session_status": result.session_status})
        return await self._apply_result(account, result)

    async def delete(self, account_id: UUID) -> Account:
        account = await self._get_account(account_id)
        activity = await self.activity_service.record_start(
            account=account,
            activity_type=ActivityType.DELETE_SESSION,
            title="Delete browser session",
        )
        try:
            result = await self.browser_manager.delete_session(account)
        except Exception as exc:
            await self.activity_service.record_failure(activity, exc)
            raise
        await self.activity_service.record_success(activity, metadata={"session_status": result.session_status})
        return await self._apply_result(account, result)

    async def open_browser(self, account_id: UUID) -> Account:
        account = await self._get_account(account_id)
        activity = await self.activity_service.record_start(
            account=account,
            activity_type=ActivityType.OPEN_BROWSER,
            title="Open browser profile",
        )
        try:
            result = await self.browser_manager.open_browser(account)
        except Exception as exc:
            await self.activity_service.record_failure(activity, exc)
            raise
        await self.activity_service.record_success(activity)
        return await self._apply_result(account, result)

    async def open_home(self, account_id: UUID) -> Account:
        account = await self._get_account(account_id)
        activity = await self.activity_service.record_start(
            account=account,
            activity_type=ActivityType.OPEN_HOME,
            target_url="https://www.reddit.com/",
            title="Open provider home",
        )
        try:
            result = await self.browser_manager.open_home(account)
        except Exception as exc:
            await self.activity_service.record_failure(activity, exc)
            raise
        await self.activity_service.record_success(activity)
        return await self._apply_result(account, result)

    async def _get_account(self, account_id: UUID) -> Account:
        account = await self.accounts.get(account_id)
        if account is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Account not found")
        return account

    async def _apply_result(self, account: Account, result: BrowserSessionResult) -> Account:
        now = datetime.now(UTC)
        account.provider = account.provider or account.platform
        account.browser_profile = account.browser_profile or account.username

        if result.storage_directory is not None:
            account.storage_directory = result.storage_directory
        elif result.session_status == "missing" and result.browser_profile_path is None:
            account.storage_directory = None

        if result.browser_profile_path is not None:
            account.browser_profile_path = result.browser_profile_path
            account.browser_profile = result.browser_profile_path
        elif result.session_status == "missing" and result.storage_directory is None:
            account.browser_profile_path = None
            account.browser_profile = None
            account.last_login = None
            account.last_validation = None

        if result.session_path is not None:
            account.session_path = result.session_path
        elif result.session_status in {"missing", "login_required"}:
            account.session_path = None

        if result.session_status is not None:
            account.session_status = result.session_status

        if result.last_login_changed:
            account.last_login = now

        if result.last_validation_changed:
            account.last_validation = now

        await self.session.commit()
        await self.session.refresh(account)
        return account
