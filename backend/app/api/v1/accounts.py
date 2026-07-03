from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.account import AccountCreate, AccountLogin, AccountRead, AccountUpdate
from app.services.account_service import AccountService
from app.services.browser_session_service import BrowserSessionService

router = APIRouter(prefix="/accounts", tags=["accounts"])


def service(session: AsyncSession = Depends(get_session)) -> AccountService:
    return AccountService(session)


def browser_session_service(session: AsyncSession = Depends(get_session)) -> BrowserSessionService:
    return BrowserSessionService(session)


@router.get("", response_model=list[AccountRead])
async def list_accounts(
    search: str | None = None,
    account_service: AccountService = Depends(service),
) -> list[AccountRead]:
    return await account_service.list_accounts(search)


@router.post("", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
async def create_account(
    payload: AccountCreate,
    account_service: AccountService = Depends(service),
) -> AccountRead:
    return await account_service.create_account(payload)


@router.get("/{account_id}", response_model=AccountRead)
async def get_account(
    account_id: UUID,
    account_service: AccountService = Depends(service),
) -> AccountRead:
    return await account_service.get_account(account_id)


@router.patch("/{account_id}", response_model=AccountRead)
async def update_account(
    account_id: UUID,
    payload: AccountUpdate,
    account_service: AccountService = Depends(service),
) -> AccountRead:
    return await account_service.update_account(account_id, payload)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: UUID,
    account_service: AccountService = Depends(service),
) -> Response:
    await account_service.delete_account(account_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{account_id}/login", response_model=AccountRead)
async def login_account(
    account_id: UUID,
    payload: AccountLogin | None = None,
    session_service: BrowserSessionService = Depends(browser_session_service),
) -> AccountRead:
    return await session_service.login(account_id, payload)


@router.post("/{account_id}/session/validate", response_model=AccountRead)
async def validate_account_session(
    account_id: UUID,
    session_service: BrowserSessionService = Depends(browser_session_service),
) -> AccountRead:
    return await session_service.validate(account_id)


@router.post("/{account_id}/session/refresh", response_model=AccountRead)
async def refresh_account_session(
    account_id: UUID,
    session_service: BrowserSessionService = Depends(browser_session_service),
) -> AccountRead:
    return await session_service.refresh(account_id)


@router.delete("/{account_id}/session", response_model=AccountRead)
async def delete_account_session(
    account_id: UUID,
    session_service: BrowserSessionService = Depends(browser_session_service),
) -> AccountRead:
    return await session_service.delete(account_id)


@router.post("/{account_id}/session/logout", response_model=AccountRead)
async def logout_account_session(
    account_id: UUID,
    session_service: BrowserSessionService = Depends(browser_session_service),
) -> AccountRead:
    return await session_service.logout(account_id)


@router.post("/{account_id}/browser/open", response_model=AccountRead)
async def open_account_browser(
    account_id: UUID,
    session_service: BrowserSessionService = Depends(browser_session_service),
) -> AccountRead:
    return await session_service.open_browser(account_id)


@router.post("/{account_id}/browser/open-home", response_model=AccountRead)
async def open_account_home(
    account_id: UUID,
    session_service: BrowserSessionService = Depends(browser_session_service),
) -> AccountRead:
    return await session_service.open_home(account_id)
