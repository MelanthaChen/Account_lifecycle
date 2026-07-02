from collections.abc import Iterable
from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.models.post import Post
from app.models.subreddit import AccountSubreddit, Subreddit


class ActivityRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_posts(self, account_id: UUID, limit: int = 50) -> list[Post]:
        query = select(Post).where(Post.account_id == account_id).order_by(desc(Post.created_utc)).limit(limit)
        return list((await self.session.scalars(query)).all())

    async def list_comments(self, account_id: UUID, limit: int = 50) -> list[Comment]:
        query = (
            select(Comment)
            .where(Comment.account_id == account_id)
            .order_by(desc(Comment.created_utc))
            .limit(limit)
        )
        return list((await self.session.scalars(query)).all())

    async def upsert_posts(self, posts: Iterable[dict]) -> None:
        rows = list(posts)
        if not rows:
            return
        statement = insert(Post).values(rows)
        await self.session.execute(
            statement.on_conflict_do_update(
                constraint="uq_posts_account_reddit_id",
                set_={
                    "title": statement.excluded.title,
                    "subreddit": statement.excluded.subreddit,
                    "url": statement.excluded.url,
                    "score": statement.excluded.score,
                    "num_comments": statement.excluded.num_comments,
                    "body": statement.excluded.body,
                },
            )
        )

    async def upsert_comments(self, comments: Iterable[dict]) -> None:
        rows = list(comments)
        if not rows:
            return
        statement = insert(Comment).values(rows)
        await self.session.execute(
            statement.on_conflict_do_update(
                constraint="uq_comments_account_reddit_id",
                set_={
                    "subreddit": statement.excluded.subreddit,
                    "body": statement.excluded.body,
                    "score": statement.excluded.score,
                    "post_id": statement.excluded.post_id,
                },
            )
        )

    async def rebuild_subreddit_activity(self, account_id: UUID) -> None:
        await self.session.execute(
            AccountSubreddit.__table__.delete().where(AccountSubreddit.account_id == account_id)
        )
        subreddit_counts = await self.session.execute(
            select(Post.subreddit, func.count(Post.id))
            .where(Post.account_id == account_id)
            .group_by(Post.subreddit)
            .union_all(
                select(Comment.subreddit, func.count(Comment.id))
                .where(Comment.account_id == account_id)
                .group_by(Comment.subreddit)
            )
        )
        counts: dict[str, int] = {}
        for name, count in subreddit_counts.all():
            counts[name] = counts.get(name, 0) + int(count)

        for name, count in counts.items():
            subreddit = await self.session.scalar(select(Subreddit).where(Subreddit.name == name))
            if subreddit is None:
                subreddit = Subreddit(name=name, display_name=f"r/{name}")
                self.session.add(subreddit)
                await self.session.flush()
            self.session.add(
                AccountSubreddit(
                    account_id=account_id,
                    subreddit_id=subreddit.id,
                    activity_count=count,
                )
            )

    async def top_subreddits(self, account_id: UUID, limit: int = 8) -> list[dict[str, int | str]]:
        query = (
            select(Subreddit.name, AccountSubreddit.activity_count)
            .join(AccountSubreddit, AccountSubreddit.subreddit_id == Subreddit.id)
            .where(AccountSubreddit.account_id == account_id)
            .order_by(desc(AccountSubreddit.activity_count))
            .limit(limit)
        )
        return [{"name": name, "activity_count": count} for name, count in (await self.session.execute(query)).all()]

    async def activity_by_day(self, account_id: UUID) -> list[dict[str, int | str]]:
        post_query = (
            select(func.date(Post.created_utc).label("day"), func.count(Post.id).label("count"))
            .where(Post.account_id == account_id)
            .group_by("day")
        )
        comment_query = (
            select(func.date(Comment.created_utc).label("day"), func.count(Comment.id).label("count"))
            .where(Comment.account_id == account_id)
            .group_by("day")
        )
        rows = (await self.session.execute(post_query.union_all(comment_query))).all()
        counts: dict[str, int] = {}
        for day, count in rows:
            key = str(day)
            counts[key] = counts.get(key, 0) + int(count)
        return [{"day": day, "activity": count} for day, count in sorted(counts.items())]
