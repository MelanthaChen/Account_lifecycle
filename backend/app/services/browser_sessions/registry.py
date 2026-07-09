from app.services.browser_sessions.base import BrowserSessionProvider


class BrowserSessionProviderRegistry:
    """Maps platform names to browser session provider implementations."""

    def get(self, platform: str) -> BrowserSessionProvider:
        """Return the provider registered for a platform name."""
        from app.providers.manager import provider_manager

        return provider_manager.get_provider(platform)


browser_session_provider_registry = BrowserSessionProviderRegistry()
