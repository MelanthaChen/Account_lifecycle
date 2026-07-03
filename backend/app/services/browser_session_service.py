from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.repositories.account_repository import AccountRepository
from app.schemas.account import AccountLogin
from app.services.browser_manager import BrowserManager
from app.services.browser_sessions.base import BrowserLoginRequest, BrowserSessionResult


class BrowserSessionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.accounts = AccountRepository(session)
        self.browser_manager = BrowserManager()

    async def login(self, account_id: UUID, payload: AccountLogin | None = None) -> Account:
        account = await self._get_account(account_id)
        login_request = self._build_login_request(account, payload)
        self._apply_login_preferences(account, payload)
        try:
            result = await self.browser_manager.login(account, login_request)
        except NotImplementedError as exc:
            raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, str(exc)) from exc
        return await self._apply_result(account, result)

    async def validate(self, account_id: UUID) -> Account:
        account = await self._get_account(account_id)
        try:
            result = await self.browser_manager.validate_session(account)
        except NotImplementedError as exc:
            raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, str(exc)) from exc
        return await self._apply_result(account, result)

    async def refresh(self, account_id: UUID) -> Account:
        account = await self._get_account(account_id)
        result = await self.browser_manager.refresh_session(account)
        return await self._apply_result(account, result)

    async def delete(self, account_id: UUID) -> Account:
        account = await self._get_account(account_id)
        result = await self.browser_manager.delete_session(account)
        return await self._apply_result(account, result)

    async def logout(self, account_id: UUID) -> Account:
        account = await self._get_account(account_id)
        result = await self.browser_manager.logout(account)
        return await self._apply_result(account, result)

    async def open_browser(self, account_id: UUID) -> Account:
        account = await self._get_account(account_id)
        result = await self.browser_manager.open_browser(account)
        return await self._apply_result(account, result)

    async def open_home(self, account_id: UUID) -> Account:
        account = await self._get_account(account_id)
        result = await self.browser_manager.open_home(account)
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
        elif result.session_status == "NOT_LOGGED_IN" and result.browser_profile_path is None:
            account.storage_directory = None

        if result.browser_profile_path is not None:
            account.browser_profile_path = result.browser_profile_path
            account.browser_profile = result.browser_profile_path
        elif result.session_status == "NOT_LOGGED_IN" and result.storage_directory is None:
            account.browser_profile_path = None
            account.browser_profile = None

        if result.session_path is not None:
            account.session_path = result.session_path
        elif result.session_status in {"missing", "NOT_LOGGED_IN"}:
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

    @staticmethod
    def _build_login_request(account: Account, payload: AccountLogin | None) -> BrowserLoginRequest:
        password = (
            payload.password
            if payload and payload.password is not None
            else account.saved_password if account.remember_credentials else None
        )
        return BrowserLoginRequest(
            username=payload.username if payload and payload.username is not None else account.saved_username,
            password=password,
            remember_credentials=(
                payload.remember_credentials
                if payload and payload.remember_credentials is not None
                else account.remember_credentials
            ),
            auto_login=payload.auto_login if payload and payload.auto_login is not None else account.auto_login,
            launch_visible_browser=(
                payload.launch_visible_browser
                if payload and payload.launch_visible_browser is not None
                else account.launch_visible_browser
            ),
        )

    @staticmethod
    def _apply_login_preferences(account: Account, payload: AccountLogin | None) -> None:
        if payload is None:
            return

        if payload.username is not None:
            account.saved_username = payload.username
        if payload.password is not None and (payload.remember_credentials or account.remember_credentials):
            account.saved_password = payload.password
        if payload.remember_credentials is not None:
            account.remember_credentials = payload.remember_credentials
            if not payload.remember_credentials:
                account.saved_password = None
        if payload.auto_login is not None:
            account.auto_login = payload.auto_login
        if payload.launch_visible_browser is not None:
            account.launch_visible_browser = payload.launch_visible_browser
