from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.health import AccountHealthRead
from app.services.health_service import HealthService

router = APIRouter(tags=["health"])


def service(session: AsyncSession = Depends(get_session)) -> HealthService:
    return HealthService(session)


@router.get("/health", response_model=list[AccountHealthRead])
async def list_health(
    health_service: HealthService = Depends(service),
) -> list[AccountHealthRead]:
    return await health_service.list_health()


@router.get("/accounts/{account_id}/health", response_model=AccountHealthRead)
async def get_account_health(
    account_id: UUID,
    health_service: HealthService = Depends(service),
) -> AccountHealthRead:
    return await health_service.get_health(account_id)


@router.post("/accounts/{account_id}/health/evaluate", response_model=AccountHealthRead)
async def evaluate_account_health(
    account_id: UUID,
    health_service: HealthService = Depends(service),
) -> AccountHealthRead:
    return await health_service.evaluate_account(account_id)


@router.post("/health/evaluate-all", response_model=list[AccountHealthRead])
async def evaluate_all_health(
    health_service: HealthService = Depends(service),
) -> list[AccountHealthRead]:
    return await health_service.evaluate_all()
