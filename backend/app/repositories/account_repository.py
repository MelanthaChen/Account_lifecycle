from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.comment import Comment
from app.models.post import Post


class AccountRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(self, *, search: str | None = None) -> list[Account]:
        query: Select[tuple[Account]] = select(Account).order_by(Account.updated_at.desc())
        if search:
            term = f"%{search.lower()}%"
            query = query.where(
                func.lower(Account.nickname).like(term)
                | func.lower(Account.reddit_username).like(term)
            )
        return list((await self.session.scalars(query)).all())

    async def get(self, account_id: UUID) -> Account | None:
        return await self.session.get(Account, account_id)

    async def get_by_username(self, username: str) -> Account | None:
        query = select(Account).where(func.lower(Account.reddit_username) == username.lower())
        return await self.session.scalar(query)

    async def create(self, account: Account) -> Account:
        self.session.add(account)
        await self.session.flush()
        return account

    async def delete(self, account: Account) -> None:
        await self.session.delete(account)

    async def totals(self, account_id: UUID) -> tuple[int, int, int]:
        post_count = await self.session.scalar(
            select(func.count(Post.id)).where(Post.account_id == account_id)
        )
        comment_count = await self.session.scalar(
            select(func.count(Comment.id)).where(Comment.account_id == account_id)
        )
        post_score = await self.session.scalar(
            select(func.coalesce(func.sum(Post.score), 0)).where(Post.account_id == account_id)
        )
        comment_score = await self.session.scalar(
            select(func.coalesce(func.sum(Comment.score), 0)).where(Comment.account_id == account_id)
        )
        return int(post_count or 0), int(comment_count or 0), int(post_score or 0) + int(comment_score or 0)
