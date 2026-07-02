from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.account import AccountAnalytics, AccountCreate, AccountRead, AccountUpdate
from app.services.account_service import AccountService

router = APIRouter(prefix="/accounts", tags=["accounts"])


def service(session: AsyncSession = Depends(get_session)) -> AccountService:
    return AccountService(session)


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


@router.get("/{account_id}/analytics", response_model=AccountAnalytics)
async def account_analytics(
    account_id: UUID,
    account_service: AccountService = Depends(service),
) -> AccountAnalytics:
    return await account_service.analytics(account_id)
