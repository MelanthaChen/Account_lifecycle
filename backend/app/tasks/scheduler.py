from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import get_settings


def create_scheduler() -> AsyncIOScheduler:
    settings = get_settings()
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(
        lambda: None,
        trigger="interval",
        minutes=settings.sync_interval_minutes,
        id="account-sync-placeholder",
        replace_existing=True,
    )
    return scheduler
