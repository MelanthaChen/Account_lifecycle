from __future__ import annotations

import asyncio
import logging
import sys

from agent import AutomationAgent
from api_client import AgentApiError
from config import load_config
from doctor import Doctor

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


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
