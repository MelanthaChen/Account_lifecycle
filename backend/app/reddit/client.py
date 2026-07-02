from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import httpx

from app.core.config import get_settings


class RedditClient:
    """Read-only Reddit JSON client for public account activity."""

    def __init__(self, http_client: httpx.AsyncClient | None = None) -> None:
        self.settings = get_settings()
        self.http_client = http_client or httpx.AsyncClient(
            base_url="https://www.reddit.com",
            headers={"User-Agent": self.settings.reddit_user_agent},
            timeout=20,
        )

    async def fetch_user_overview(self, username: str, limit: int = 50) -> list[dict[str, Any]]:
        response = await self.http_client.get(f"/user/{username}/overview.json", params={"limit": limit})
        response.raise_for_status()
        payload = response.json()
        return [item["data"] for item in payload.get("data", {}).get("children", [])]

    @staticmethod
    def normalize_overview_items(account_id: UUID, items: list[dict[str, Any]]) -> tuple[list[dict], list[dict]]:
        posts: list[dict] = []
        comments: list[dict] = []
        for item in items:
            created = datetime.fromtimestamp(float(item.get("created_utc", 0)), tz=UTC)
            kind = item.get("kind") or item.get("name", "").split("_", 1)[0]
            if kind == "t3" or "title" in item:
                posts.append(
                    {
                        "reddit_id": item["id"],
                        "account_id": account_id,
                        "title": item.get("title") or "(untitled)",
                        "subreddit": item.get("subreddit") or "unknown",
                        "url": item.get("url"),
                        "score": int(item.get("score") or 0),
                        "num_comments": int(item.get("num_comments") or 0),
                        "created_utc": created,
                        "body": item.get("selftext"),
                    }
                )
            elif kind == "t1" or "body" in item:
                comments.append(
                    {
                        "reddit_id": item["id"],
                        "account_id": account_id,
                        "post_id": None,
                        "subreddit": item.get("subreddit") or "unknown",
                        "body": item.get("body"),
                        "score": int(item.get("score") or 0),
                        "created_utc": created,
                    }
                )
        return posts, comments

    async def aclose(self) -> None:
        await self.http_client.aclose()
