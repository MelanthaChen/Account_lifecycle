from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, HttpUrl, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.services.upvote_service import UpvoteService, UpvoteExecutionResult

router = APIRouter(prefix="/upvote", tags=["upvote"])


class UpvoteRequest(BaseModel):
    account_ids: list[UUID] = Field(min_length=1)
    target_url: HttpUrl

    @field_validator("target_url")
    @classmethod
    def validate_reddit_url(cls, value: HttpUrl) -> HttpUrl:
        host = (value.host or "").lower()
        if host not in {"reddit.com", "www.reddit.com", "old.reddit.com"}:
            raise ValueError("target_url must be a Reddit URL")
        return value


class UpvoteResult(BaseModel):
    account: str
    opened: bool
    clicked: bool
    verified: bool
    reason: str | None = None


class UpvoteResponse(BaseModel):
    success: bool
    results: list[UpvoteResult]


def service(session: AsyncSession = Depends(get_session)) -> UpvoteService:
    return UpvoteService(session)


@router.post("", response_model=UpvoteResponse)
async def create_upvote_request(
    payload: UpvoteRequest,
    upvote_service: UpvoteService = Depends(service),
) -> UpvoteResponse:
    results = await upvote_service.open_target_for_accounts(
        account_ids=payload.account_ids,
        target_url=str(payload.target_url),
    )
    return UpvoteResponse(
        success=True,
        results=[_serialize_result(result) for result in results],
    )


def _serialize_result(result: UpvoteExecutionResult) -> UpvoteResult:
    return UpvoteResult(
        account=result.account,
        opened=result.opened,
        clicked=result.clicked,
        verified=result.verified,
        reason=result.reason,
    )
