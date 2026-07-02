from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PostRead(BaseModel):
    id: UUID
    reddit_id: str
    account_id: UUID
    title: str
    subreddit: str
    url: str | None
    score: int
    num_comments: int
    created_utc: datetime
    body: str | None

    model_config = ConfigDict(from_attributes=True)


class CommentRead(BaseModel):
    id: UUID
    reddit_id: str
    account_id: UUID
    post_id: UUID | None
    subreddit: str
    body: str | None
    score: int
    created_utc: datetime

    model_config = ConfigDict(from_attributes=True)
