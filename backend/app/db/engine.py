from __future__ import annotations

from typing import Any

from sqlalchemy.engine import URL, make_url


def asyncpg_engine_options(database_url: str) -> dict[str, Any]:
    """Return SQLAlchemy async engine options compatible with asyncpg.

    Hosted PostgreSQL providers such as Neon commonly expose libpq-style URLs
    with `sslmode=require`. asyncpg does not accept `sslmode` as a connection
    keyword, so SQLAlchemy passes it through and startup fails. This helper
    translates that query parameter into asyncpg's supported `ssl` connect arg.
    """
    url = make_url(database_url)
    connect_args: dict[str, Any] = {}

    if url.drivername == "postgresql+asyncpg":
        sslmode = url.query.get("sslmode")
        if sslmode is not None:
            url = _remove_query_param(url, "sslmode")
            if sslmode.lower() != "disable":
                connect_args["ssl"] = True

    options: dict[str, Any] = {"url": url, "pool_pre_ping": True}
    if connect_args:
        options["connect_args"] = connect_args
    return options


def render_database_url_for_alembic(database_url: str) -> str:
    """Return a database URL string safe for Alembic offline rendering."""
    url = asyncpg_engine_options(database_url)["url"]
    return url.render_as_string(hide_password=False)


def _remove_query_param(url: URL, key: str) -> URL:
    query = dict(url.query)
    query.pop(key, None)
    return url.set(query=query)
