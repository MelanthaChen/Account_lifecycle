from __future__ import annotations

import asyncio
import shutil
import sys
from pathlib import Path

import httpx

from api_client import AgentApiClient
from config import AgentConfig
from providers.manager import provider_manager
from runtime_types import Platform


class Doctor:
    """Runs setup checks for the Automation Agent."""

    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self.api = AgentApiClient(config)
        self.passed = 0
        self.failed = 0

    async def run(self) -> int:
        print("Automation Agent Doctor")
        print(f"Backend: {self.config.backend_url}\n")
        await self._check("Python 3.12+", self._python_version)
        await self._check("uv", self._uv)
        await self._check("Dependencies", self._dependencies)
        await self._check("Backend reachable", self._backend_reachable)
        await self._check("Authentication", self._authentication)
        await self._check("Heartbeat", self._heartbeat)
        await self._check("Queue API", self._queue_api)
        await self._check("Playwright", self._playwright_import)
        await self._check("Chromium", self._chromium)
        await self._check("Storage directory", self._storage_directory)
        await self._check("Profile directory", self._profile_directory)
        await self._check("Reddit provider", self._reddit_provider)
        await self._check("Browser launch", self._browser_launch)

        print("\nSummary")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        if self.failed:
            print("\nSome checks failed. See docs/automation-agent-installation.md.")
            return 1
        print("\nAutomation Agent is ready.")
        return 0

    async def _check(self, label: str, check) -> None:
        try:
            await check()
        except Exception as exc:
            self.failed += 1
            print(f"✗ {label}: {exc}")
            return
        self.passed += 1
        print(f"✓ {label}")

    async def _python_version(self) -> None:
        current = tuple(int(part) for part in sys.version.split()[0].split(".")[:2])
        if current < (3, 12):
            raise RuntimeError(f"Python 3.12 or newer is required. Current: {sys.version.split()[0]}")

    async def _uv(self) -> None:
        if shutil.which("uv") is None:
            raise RuntimeError("uv is not installed. Double-click Install.command.")

    async def _dependencies(self) -> None:
        process = await asyncio.create_subprocess_exec(
            "uv",
            "run",
            "python",
            "-c",
            "import httpx, yaml, playwright",
            cwd=Path(__file__).resolve().parent,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
        if process.returncode != 0:
            raise RuntimeError("Python dependencies are missing. Double-click Install.command.")

    async def _backend_reachable(self) -> None:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(self.config.backend_url.rstrip("/") + "/agent/heartbeat")
            if response.status_code >= 500:
                response.raise_for_status()

    async def _authentication(self) -> None:
        await self.api.heartbeat(hostname="doctor", status="IDLE", running_job=None)

    async def _heartbeat(self) -> None:
        await self.api.heartbeat(hostname="doctor", status="IDLE", running_job=None)

    async def _queue_api(self) -> None:
        await self.api.next_job()

    async def _playwright_import(self) -> None:
        from playwright.async_api import async_playwright  # noqa: F401

    async def _chromium(self) -> None:
        from playwright.async_api import async_playwright

        playwright = await async_playwright().start()
        try:
            browser = await playwright.chromium.launch(headless=True)
            await browser.close()
        finally:
            await playwright.stop()

    async def _storage_directory(self) -> None:
        self.config.profile_root.mkdir(parents=True, exist_ok=True)
        self._assert_writable(self.config.profile_root)

    async def _profile_directory(self) -> None:
        profile_directory = self.config.profile_root / "reddit"
        profile_directory.mkdir(parents=True, exist_ok=True)
        self._assert_writable(profile_directory)

    async def _reddit_provider(self) -> None:
        provider_manager.get_provider(Platform.REDDIT)

    async def _browser_launch(self) -> None:
        from playwright.async_api import async_playwright

        playwright = await async_playwright().start()
        try:
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto("about:blank")
            await browser.close()
        finally:
            await playwright.stop()

    @staticmethod
    def _assert_writable(path: Path) -> None:
        probe = path / ".agent-doctor-write-test"
        probe.write_text("ok")
        probe.unlink()
