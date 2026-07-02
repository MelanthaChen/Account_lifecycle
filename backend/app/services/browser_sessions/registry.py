from app.services.browser_sessions.base import BrowserSessionProvider
from app.services.browser_sessions.reddit import RedditSessionProvider


class BrowserSessionProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, BrowserSessionProvider] = {
            RedditSessionProvider.platform: RedditSessionProvider(),
        }

    def get(self, platform: str) -> BrowserSessionProvider:
        provider = self._providers.get(platform.lower())

        if provider is None:
            raise ValueError(f"Unsupported browser session provider: {platform}")

        return provider


browser_session_provider_registry = BrowserSessionProviderRegistry()
