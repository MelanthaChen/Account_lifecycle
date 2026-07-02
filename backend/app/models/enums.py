from enum import StrEnum


class AccountStatus(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    ARCHIVED = "archived"


class Platform(StrEnum):
    REDDIT = "reddit"
