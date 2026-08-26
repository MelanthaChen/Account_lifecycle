from __future__ import annotations

import asyncio
import logging
import shutil
import sys

from agent import AutomationAgent
from api_client import AgentApiError
from config import load_config
from doctor import Doctor

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)


async def main() -> None:
    config = load_config()
    if len(sys.argv) > 1 and sys.argv[1] == "doctor":
        raise SystemExit(await Doctor(config).run())
    agent = AutomationAgent(config)
    await agent.run_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except AgentApiError as exc:
        raise SystemExit(f"\n{exc}\n") from None
    except KeyboardInterrupt:
        raise SystemExit("\nAutomation Agent stopped. You can close this window.\n") from None
    except SystemExit:
        raise
    except Exception as exc:
        message = str(exc)
        if "Executable doesn't exist" in message or "playwright install" in message:
            raise SystemExit(
                "\nBrowser installation missing.\n\n"
                "Please run:\n"
                "uv run playwright install chromium\n\n"
                "Or double-click Install.command again.\n"
            ) from None
        if shutil.which("uv") is None:
            raise SystemExit(
                "\nuv is not installed.\n\n"
                "Please double-click Install.command to install dependencies.\n"
            ) from None
        raise
