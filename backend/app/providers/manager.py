from __future__ import annotations

from app.models.enums import Platform
from app.providers.base import Provider
from app.providers.reddit.provider import RedditProvider


class ProviderManager:
    """Resolves account platforms to their provider implementation."""

    def __init__(self) -> None:
        reddit = RedditProvider()
        self._providers: dict[Platform, Provider] = {
            reddit.platform_name: reddit,
        }

    def get_provider(self, platform: Platform | str) -> Provider:
        """Return the registered provider for a platform enum or value."""
        platform_value = Platform(platform)
        provider = self._providers.get(platform_value)
        if provider is None:
            raise ValueError(f"Unsupported provider: {platform}")
        return provider


provider_manager = ProviderManager()
