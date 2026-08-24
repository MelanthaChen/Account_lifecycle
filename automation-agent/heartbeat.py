from __future__ import annotations

import asyncio
import logging
import socket

import httpx

from api_client import AgentApiClient, AgentApiError
from config import AgentConfig

logger = logging.getLogger("automation-agent")


class HeartbeatLoop:
    """Periodically posts single Automation Agent state to the backend."""

    def __init__(self, config: AgentConfig, api: AgentApiClient) -> None:
        self.config = config
        self.api = api
        self.hostname = socket.gethostname()
        self.running_job: str | None = None
        self.online = False

    async def run_forever(self) -> None:
        while True:
            await self.post_once()
            await asyncio.sleep(self.config.heartbeat_interval)

    async def post_once(self) -> None:
        try:
            await self.api.heartbeat(
                hostname=self.hostname,
                status="RUNNING" if self.running_job else "IDLE",
                running_job=self.running_job,
            )
            self.online = True
        except (AgentApiError, httpx.HTTPError, TimeoutError, OSError):
            logger.warning("Heartbeat failed; will retry.")
