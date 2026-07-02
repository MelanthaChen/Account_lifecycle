from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.sync_job import SyncJobRead
from app.services.sync_service import SyncService

router = APIRouter(prefix="/accounts/{account_id}/sync", tags=["sync"])


def service(session: AsyncSession = Depends(get_session)) -> SyncService:
    return SyncService(session)


@router.post("", response_model=SyncJobRead)
async def sync_account(
    account_id: UUID,
    sync_service: SyncService = Depends(service),
) -> SyncJobRead:
    return await sync_service.sync_account(account_id)


@router.get("/jobs", response_model=list[SyncJobRead])
async def list_sync_jobs(
    account_id: UUID,
    sync_service: SyncService = Depends(service),
) -> list[SyncJobRead]:
    return await sync_service.list_jobs(account_id)
