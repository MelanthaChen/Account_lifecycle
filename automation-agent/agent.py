from __future__ import annotations

import asyncio
import logging

import httpx

from api_client import AgentApiClient, AgentApiError, BackendVersionError
from config import AgentConfig
from executor import WorkflowExecutor
from heartbeat import HeartbeatLoop

logger = logging.getLogger("automation-agent")


class AutomationAgent:
    """Polls remote backend jobs and executes them locally."""

    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self.api = AgentApiClient(config)
        self.executor = WorkflowExecutor(config)
        self.heartbeat = HeartbeatLoop(config, self.api)

    async def run_forever(self) -> None:
        self._print_connecting_banner()
        await self.heartbeat.post_once()
        self._print_online_banner()
        heartbeat_task = asyncio.create_task(self.heartbeat.run_forever())
        try:
            await self._poll_forever()
        finally:
            heartbeat_task.cancel()

    async def _poll_forever(self) -> None:
        backoff = self.config.poll_interval
        while True:
            try:
                did_work = await self._poll_once()
                backoff = self.config.poll_interval
                await asyncio.sleep(0 if did_work else self.config.poll_interval)
            except (AgentApiError, BackendVersionError) as exc:
                print(f"\n{exc}\n")
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 60)
            except (httpx.HTTPError, TimeoutError, OSError):
                logger.warning("Backend unavailable; retrying in %.1f seconds.", backoff)
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 60)
            except Exception:
                logger.exception("Unexpected agent error; continuing.")
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 60)

    async def _poll_once(self) -> bool:
        job = await self.api.next_job()
        if job is None:
            logger.info("No queued jobs.")
            return False

        job_id = job["id"]
        self.heartbeat.running_job = job_id
        logger.info("Claiming job %s", job_id)
        await self.api.start_job(job_id)
        try:
            result = await self.executor.execute_job(job)
        except Exception as exc:
            logger.exception("Job %s failed.", job_id)
            await self.api.fail_job(job_id, str(exc), {"success": False, "error": str(exc)})
            return True
        finally:
            self.heartbeat.running_job = None

        if result["success"]:
            await self.api.finish_job(job_id, result)
        else:
            await self.api.fail_job(job_id, "workflow_failed", result)
        return True

    def _print_connecting_banner(self) -> None:
        print(
            "\n".join(
                [
                    "==================================",
                    "Automation Agent",
                    f"Backend: {self.config.backend_url}",
                    "Status: Connecting...",
                    "==================================",
                ]
            )
        )

    def _print_online_banner(self) -> None:
        print(
            "\n".join(
                [
                    "Automation Agent",
                    "Status: Online",
                    f"Polling: Every {self.config.poll_interval:g} seconds",
                    "Browser: Ready",
                    "Queue: Waiting for jobs",
                    "",
                ]
            )
        )
