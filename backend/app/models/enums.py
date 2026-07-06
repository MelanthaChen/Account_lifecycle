from enum import StrEnum


class AccountStatus(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    ARCHIVED = "archived"


class Platform(StrEnum):
    REDDIT = "reddit"


class ActivityStatus(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ActivityType(StrEnum):
    LOGIN = "LOGIN"
    OPEN_BROWSER = "OPEN_BROWSER"
    OPEN_HOME = "OPEN_HOME"
    BROWSE = "BROWSE"
    UPVOTE = "UPVOTE"
    DOWNVOTE = "DOWNVOTE"
    COMMENT = "COMMENT"
    POST = "POST"
    JOIN_SUBREDDIT = "JOIN_SUBREDDIT"
    LEAVE_SUBREDDIT = "LEAVE_SUBREDDIT"
    SYNC_PROFILE = "SYNC_PROFILE"
    VALIDATE_SESSION = "VALIDATE_SESSION"
    REFRESH_SESSION = "REFRESH_SESSION"
    DELETE_SESSION = "DELETE_SESSION"
