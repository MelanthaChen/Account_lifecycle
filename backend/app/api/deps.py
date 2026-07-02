from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.services.account_service import AccountService
from app.services.activity_service import ActivityService
from app.services.sync_service import SyncService


async def get_account_service(
    session: AsyncSession = Depends(get_session),
) -> AsyncGenerator[AccountService, None]:
    yield AccountService(session)


async def get_activity_service(
    session: AsyncSession = Depends(get_session),
) -> AsyncGenerator[ActivityService, None]:
    yield ActivityService(session)


async def get_sync_service(
    session: AsyncSession = Depends(get_session),
) -> AsyncGenerator[SyncService, None]:
    yield SyncService(session)
