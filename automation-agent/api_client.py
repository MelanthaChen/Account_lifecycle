from __future__ import annotations

from typing import Any

import httpx

from config import AgentConfig

INSTALL_DOC = "docs/automation-agent-installation.md"


class AgentApiError(RuntimeError):
    """User-friendly backend communication error."""


class BackendVersionError(AgentApiError):
    """Raised when the backend does not expose the expected agent API."""


class AgentApiClient:
    """HTTP client for remote backend job and heartbeat APIs."""

    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self.client = httpx.AsyncClient(
            base_url=config.backend_url.rstrip("/"),
            timeout=httpx.Timeout(connect=10.0, read=60.0, write=30.0, pool=10.0),
            headers={
                "X-Agent-Name": config.agent_name,
                "X-Agent-Secret": config.agent_secret,
            },
        )

    async def next_job(self) -> dict[str, Any] | None:
        response = await self.client.get("/jobs/next")
        if response.status_code == 204:
            return None
        self._raise_for_status(response)
        return response.json()

    async def start_job(self, job_id: str) -> dict[str, Any]:
        return await self._post(f"/jobs/{job_id}/start", {})

    async def finish_job(self, job_id: str, result_json: dict[str, Any]) -> dict[str, Any]:
        return await self._post(
            f"/jobs/{job_id}/finish",
            {"result_json": result_json},
        )

    async def fail_job(self, job_id: str, error: str, result_json: dict[str, Any] | None = None) -> dict[str, Any]:
        return await self._post(
            f"/jobs/{job_id}/fail",
            {
                "error": error,
                "result_json": result_json,
            },
        )

    async def heartbeat(self, *, hostname: str, status: str, running_job: str | None) -> dict[str, Any]:
        return await self._post(
            "/agent/heartbeat",
            {"hostname": hostname, "status": status, "running_job": running_job},
        )

    async def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = await self.client.post(path, json=payload)
        self._raise_for_status(response)
        return response.json()

    def _raise_for_status(self, response: httpx.Response) -> None:
        if response.status_code in {401, 403}:
            raise AgentApiError(
                "Authentication failed.\n\n"
                "Please check:\n"
                "- agent_name\n"
                "- agent_secret\n"
                "- backend_url\n\n"
                f"See: {INSTALL_DOC}"
            )
        if response.status_code == 404:
            raise BackendVersionError(
                "The backend does not support this Automation Agent version.\n\n"
                "Please update the Render deployment."
            )
        response.raise_for_status()
