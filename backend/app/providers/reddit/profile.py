from __future__ import annotations

from dataclasses import dataclass
import re

from app.models.account import Account
from app.providers.base import ProviderProfileData
from app.providers.reddit.session import RedditSessionProvider


@dataclass(frozen=True)
class RedditProfileData(ProviderProfileData):
    display_name: str | None = None
    provider_username: str | None = None
    avatar_url: str | None = None
    karma_post: int | None = None
    karma_comment: int | None = None
    cake_day: str | None = None
    verified_email: bool | None = None
    is_nsfw: bool | None = None
    is_moderator: bool | None = None
    is_gold: bool | None = None


class RedditProfileService:
    """Scrapes Reddit profile attributes using an account's persistent browser profile."""

    def __init__(self, session_provider: RedditSessionProvider) -> None:
        self.session_provider = session_provider

    async def sync_profile(self, account: Account) -> RedditProfileData:
        """Open the account profile page and extract available profile fields."""
        active_session = await self.session_provider.open_persistent_context(
            account,
            headless=not account.launch_visible_browser,
        )
        try:
            context = active_session.context
            page = context.pages[0] if context.pages else await context.new_page()
            profile_url = f"https://www.reddit.com/user/{account.username}/"
            await page.goto(profile_url, wait_until="domcontentloaded")
            await page.wait_for_timeout(2500)
            return await self._extract_profile(page, account)
        finally:
            await self.session_provider.close_session(active_session)

    async def _extract_profile(self, page, account: Account) -> RedditProfileData:
        snapshot = await page.evaluate(
            """
            () => {
              const text = document.body?.innerText || "";
              const meta = (selector) => document.querySelector(selector)?.getAttribute("content") || null;
              const attr = (selector, name) => document.querySelector(selector)?.getAttribute(name) || null;
              return {
                text,
                title: document.title || null,
                ogTitle: meta('meta[property="og:title"]'),
                ogImage: meta('meta[property="og:image"]'),
                displayName:
                  attr("shreddit-profile-header", "display-name") ||
                  attr("shreddit-profile-header", "name") ||
                  null,
                avatarUrl:
                  attr("shreddit-profile-header", "icon") ||
                  attr("shreddit-profile-header", "avatar") ||
                  meta('meta[property="og:image"]')
              };
            }
            """
        )

        text = snapshot.get("text") or ""
        return RedditProfileData(
            display_name=self._clean_display_name(
                snapshot.get("displayName") or self._display_name_from_title(snapshot.get("ogTitle") or snapshot.get("title"))
            ),
            provider_username=self._extract_username(text, account),
            avatar_url=self._clean_url(snapshot.get("avatarUrl") or snapshot.get("ogImage")),
            karma_post=self._extract_labeled_number(text, "Post Karma"),
            karma_comment=self._extract_labeled_number(text, "Comment Karma"),
            cake_day=self._extract_cake_day(text),
            verified_email=self._extract_flag(text, ["Verified Email", "Email Verified"]),
            is_nsfw=self._extract_flag(text, ["NSFW", "Not Safe For Work", "Not Safe for Work"]),
            is_moderator=self._extract_flag(text, ["Moderator", "Mod of"]),
            is_gold=self._extract_flag(text, ["Reddit Premium", "Premium", "Reddit Gold"]),
        )

    @staticmethod
    def _extract_username(text: str, account: Account) -> str:
        match = re.search(r"u/([A-Za-z0-9_-]+)", text)
        return match.group(1) if match else account.username

    @staticmethod
    def _display_name_from_title(value: str | None) -> str | None:
        if not value:
            return None
        return value.split(" - Reddit", 1)[0].strip() or None

    @staticmethod
    def _clean_display_name(value: str | None) -> str | None:
        if not value:
            return None
        return value.strip() or None

    @staticmethod
    def _clean_url(value: str | None) -> str | None:
        if not value:
            return None
        value = value.strip()
        return value if value.startswith(("http://", "https://")) else None

    @staticmethod
    def _extract_labeled_number(text: str, label: str) -> int | None:
        patterns = [
            rf"([\d,\.]+)\s+{re.escape(label)}",
            rf"{re.escape(label)}\s+([\d,\.]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return RedditProfileService._parse_number(match.group(1))
        return None

    @staticmethod
    def _parse_number(value: str) -> int | None:
        cleaned = value.replace(",", "").replace(".", "")
        return int(cleaned) if cleaned.isdigit() else None

    @staticmethod
    def _extract_cake_day(text: str) -> str | None:
        match = re.search(r"Cake day\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})", text, flags=re.IGNORECASE)
        return match.group(1) if match else None

    @staticmethod
    def _extract_flag(text: str, labels: list[str]) -> bool | None:
        lowered = text.lower()
        return True if any(label.lower() in lowered for label in labels) else None
