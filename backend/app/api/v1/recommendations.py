from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.recommendation import AccountRecommendationRead
from app.services.recommendation_service import RecommendationService

router = APIRouter(tags=["recommendations"])


def service(session: AsyncSession = Depends(get_session)) -> RecommendationService:
    return RecommendationService(session)


@router.get("/recommendations", response_model=list[AccountRecommendationRead])
async def list_recommendations(
    recommendation_service: RecommendationService = Depends(service),
) -> list[AccountRecommendationRead]:
    return await recommendation_service.list_recommendations()


@router.get("/accounts/{account_id}/recommendations", response_model=list[AccountRecommendationRead])
async def list_account_recommendations(
    account_id: UUID,
    recommendation_service: RecommendationService = Depends(service),
) -> list[AccountRecommendationRead]:
    return await recommendation_service.list_for_account(account_id)


@router.post("/recommendations/evaluate-all", response_model=list[AccountRecommendationRead])
async def evaluate_all_recommendations(
    recommendation_service: RecommendationService = Depends(service),
) -> list[AccountRecommendationRead]:
    return await recommendation_service.evaluate_all()


@router.post("/accounts/{account_id}/recommendations/evaluate", response_model=list[AccountRecommendationRead])
async def evaluate_account_recommendations(
    account_id: UUID,
    recommendation_service: RecommendationService = Depends(service),
) -> list[AccountRecommendationRead]:
    return await recommendation_service.evaluate_account(account_id)


@router.post("/recommendations/{recommendation_id}/dismiss", response_model=AccountRecommendationRead)
async def dismiss_recommendation(
    recommendation_id: UUID,
    recommendation_service: RecommendationService = Depends(service),
) -> AccountRecommendationRead:
    return await recommendation_service.dismiss(recommendation_id)
