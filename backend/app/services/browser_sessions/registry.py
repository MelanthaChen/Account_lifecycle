from app.services.browser_sessions.base import BrowserSessionProvider
from app.services.browser_sessions.reddit import RedditSessionProvider


class BrowserSessionProviderRegistry:
    """Maps platform names to browser session provider implementations."""

    def __init__(self) -> None:
        self._providers: dict[str, BrowserSessionProvider] = {
            RedditSessionProvider.platform: RedditSessionProvider(),
        }

    def get(self, platform: str) -> BrowserSessionProvider:
        """Return the provider registered for a platform name."""
        provider = self._providers.get(platform.lower())

        if provider is None:
            raise ValueError(f"Unsupported browser session provider: {platform}")

        return provider


browser_session_provider_registry = BrowserSessionProviderRegistry()
