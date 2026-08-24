from __future__ import annotations

from enum import StrEnum
from typing import Protocol
from uuid import UUID


class Platform(StrEnum):
    REDDIT = "reddit"


class WorkflowActionType(StrEnum):
    OPEN_URL = "OPEN_URL"
    WAIT = "WAIT"
    SCROLL = "SCROLL"
    OPEN_POST = "OPEN_POST"
    BACK = "BACK"
    COMMENT = "COMMENT"
    UPVOTE = "UPVOTE"


class AccountLike(Protocol):
    id: UUID
    nickname: str
    username: str
    platform: Platform | str
    session_path: str | None
    storage_directory: str | None
    browser_profile_path: str | None
    launch_visible_browser: bool
