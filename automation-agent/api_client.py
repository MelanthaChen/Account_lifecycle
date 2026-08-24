from __future__ import annotations

from typing import Any

import httpx

from config import AgentConfig


class AgentApiClient:
    """HTTP client for remote backend job and heartbeat APIs."""

    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self.client = httpx.AsyncClient(
            base_url=config.backend_url.rstrip("/"),
            timeout=httpx.Timeout(connect=10.0, read=60.0, write=30.0, pool=10.0),
            headers={
                "X-Worker-Id": config.worker_id,
                "X-Worker-Secret": config.worker_secret,
            },
        )

    async def next_job(self) -> dict[str, Any] | None:
        response = await self.client.get("/jobs/next")
        if response.status_code == 204:
            return None
        response.raise_for_status()
        return response.json()

    async def start_job(self, job_id: str) -> dict[str, Any]:
        return await self._post(f"/jobs/{job_id}/start", {"worker_id": self.config.worker_id})

    async def finish_job(self, job_id: str, result_json: dict[str, Any]) -> dict[str, Any]:
        return await self._post(
            f"/jobs/{job_id}/finish",
            {"worker_id": self.config.worker_id, "result_json": result_json},
        )

    async def fail_job(self, job_id: str, error: str, result_json: dict[str, Any] | None = None) -> dict[str, Any]:
        return await self._post(
            f"/jobs/{job_id}/fail",
            {
                "worker_id": self.config.worker_id,
                "error": error,
                "result_json": result_json,
            },
        )

    async def heartbeat(self, *, hostname: str, status: str, running_job: str | None) -> dict[str, Any]:
        return await self._post(
            "/workers/heartbeat",
            {"hostname": hostname, "status": status, "running_job": running_job},
        )

    async def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = await self.client.post(path, json=payload)
        response.raise_for_status()
        return response.json()
