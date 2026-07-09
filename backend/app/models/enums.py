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


class CampaignActionType(StrEnum):
    UPVOTE = "UPVOTE"


class CampaignStatus(StrEnum):
    DRAFT = "Draft"
    READY = "Ready"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"


class ScheduleType(StrEnum):
    ONCE = "ONCE"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    CUSTOM_CRON = "CUSTOM_CRON"


class WorkflowActionType(StrEnum):
    OPEN_URL = "OPEN_URL"
    WAIT = "WAIT"
    SCROLL = "SCROLL"
    OPEN_POST = "OPEN_POST"
    BACK = "BACK"
    UPVOTE = "UPVOTE"


class HealthStatus(StrEnum):
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class RiskLevel(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RecommendationStatus(StrEnum):
    ACTIVE = "ACTIVE"
    DISMISSED = "DISMISSED"
    COMPLETED = "COMPLETED"


class RecommendationPriority(StrEnum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RecommendationType(StrEnum):
    RUN_WARM_UP = "RUN_WARM_UP"
    RUN_QUICK_UPVOTE = "RUN_QUICK_UPVOTE"
    RUN_CASUAL_READER = "RUN_CASUAL_READER"
    RUN_DEEP_READER = "RUN_DEEP_READER"
    SYNC_PROFILE = "SYNC_PROFILE"
    REFRESH_SESSION = "REFRESH_SESSION"
    NO_ACTION = "NO_ACTION"
