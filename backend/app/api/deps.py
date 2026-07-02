from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.services.account_service import AccountService


async def get_account_service(
    session: AsyncSession = Depends(get_session),
) -> AsyncGenerator[AccountService, None]:
    yield AccountService(session)
