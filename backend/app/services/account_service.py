from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.enums import ActivityType
from app.providers.manager import provider_manager
from app.repositories.account_repository import AccountRepository
from app.schemas.account import AccountCreate, AccountUpdate
from app.services.activity_service import ActivityService


class AccountService:
    """Coordinates account CRUD and provider-backed profile synchronization."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.accounts = AccountRepository(session)
        self.activity_service = ActivityService(session)

    async def list_accounts(self, search: str | None = None) -> list[Account]:
        """Return managed accounts, optionally filtered by nickname or username."""
        return await self.accounts.list(search=search)

    async def get_account(self, account_id: UUID) -> Account:
        """Return one account or raise 404 when it does not exist."""
        account = await self.accounts.get(account_id)
        if account is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Account not found")
        return account

    async def create_account(self, payload: AccountCreate) -> Account:
        """Create a unique managed account for a platform and username."""
        existing = await self.accounts.get_by_platform_username(payload.platform, payload.username)
        if existing is not None:
            raise HTTPException(status.HTTP_409_CONFLICT, "Account username is already managed")
        account = Account(**payload.model_dump())
        await self.accounts.create(account)
        await self.session.commit()
        await self.session.refresh(account)
        return account

    async def update_account(self, account_id: UUID, payload: AccountUpdate) -> Account:
        """Apply partial account updates while preserving platform/username uniqueness."""
        account = await self.get_account(account_id)
        values = payload.model_dump(exclude_unset=True)
        platform = values.get("platform", account.platform)
        username = values.get("username", account.username)
        if "platform" in values or "username" in values:
            existing = await self.accounts.get_by_platform_username(platform, username)
            if existing is not None and existing.id != account_id:
                raise HTTPException(status.HTTP_409_CONFLICT, "Account username is already managed")
        for key, value in values.items():
            setattr(account, key, value)
        await self.session.commit()
        await self.session.refresh(account)
        return account

    async def delete_account(self, account_id: UUID) -> None:
        """Delete an account record and cascade dependent database rows."""
        account = await self.get_account(account_id)
        await self.accounts.delete(account)
        await self.session.commit()

    async def sync_profile(self, account_id: UUID) -> Account:
        """Scrape the provider profile through the stored browser profile and persist fields."""
        account = await self.get_account(account_id)
        provider = provider_manager.get_provider(account.platform)

        activity = await self.activity_service.record_start(
            account=account,
            activity_type=ActivityType.SYNC_PROFILE,
            target_url=f"{provider.home_url.rstrip('/')}/user/{account.username}/",
            title=f"Sync {provider.display_name} profile",
        )
        try:
            profile = await provider.sync_profile(account)
        except Exception as exc:
            await self.activity_service.record_failure(activity, exc)
            raise
        account.display_name = profile.display_name
        account.reddit_username = profile.provider_username
        account.avatar_url = profile.avatar_url
        account.karma_post = profile.karma_post
        account.karma_comment = profile.karma_comment
        account.cake_day = profile.cake_day
        account.verified_email = profile.verified_email
        account.is_nsfw = profile.is_nsfw
        account.is_moderator = profile.is_moderator
        account.is_gold = profile.is_gold
        account.last_profile_sync = datetime.now(UTC)
        await self.activity_service.record_success(
            activity,
            metadata={
                "provider_username": profile.provider_username,
                "display_name": profile.display_name,
            },
        )
        await self.session.commit()
        await self.session.refresh(account)
        return account
