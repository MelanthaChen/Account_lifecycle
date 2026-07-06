from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel, HttpUrl

router = APIRouter(prefix="/upvote", tags=["upvote"])


class UpvoteRequest(BaseModel):
    account_id: UUID
    target_url: HttpUrl


class UpvoteResponse(BaseModel):
    status: str
    target_url: str
    account_id: UUID


@router.post("", response_model=UpvoteResponse)
async def create_upvote_request(payload: UpvoteRequest) -> UpvoteResponse:
    return UpvoteResponse(
        status="received",
        target_url=str(payload.target_url),
        account_id=payload.account_id,
    )
