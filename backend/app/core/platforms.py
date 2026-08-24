from app.models.enums import Platform, WorkflowActionType

PROVIDER_HOME_URLS: dict[Platform, str] = {
    Platform.REDDIT: "https://www.reddit.com/",
}

PROVIDER_DISPLAY_NAMES: dict[Platform, str] = {
    Platform.REDDIT: "Reddit",
}

SUPPORTED_WORKFLOW_ACTIONS: dict[Platform, set[WorkflowActionType]] = {
    Platform.REDDIT: {
        WorkflowActionType.OPEN_URL,
        WorkflowActionType.WAIT,
        WorkflowActionType.SCROLL,
        WorkflowActionType.OPEN_POST,
        WorkflowActionType.BACK,
        WorkflowActionType.COMMENT,
        WorkflowActionType.UPVOTE,
    },
}


def provider_home_url(platform: Platform | str) -> str:
    return PROVIDER_HOME_URLS[Platform(platform)]


def provider_display_name(platform: Platform | str) -> str:
    return PROVIDER_DISPLAY_NAMES[Platform(platform)]


def supported_workflow_actions(platform: Platform | str) -> set[WorkflowActionType]:
    return SUPPORTED_WORKFLOW_ACTIONS[Platform(platform)]
