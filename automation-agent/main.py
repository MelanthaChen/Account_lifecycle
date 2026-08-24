from __future__ import annotations

import asyncio
import logging

from agent import AutomationAgent
from config import load_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


async def main() -> None:
    agent = AutomationAgent(load_config())
    await agent.run_forever()


if __name__ == "__main__":
    asyncio.run(main())
