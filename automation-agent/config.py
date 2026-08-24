from __future__ import annotations

from dataclasses import dataclass
from getpass import getpass
from pathlib import Path

AGENT_ROOT = Path(__file__).resolve().parent
CONFIG_PATH = AGENT_ROOT / "agent.yaml"
DEFAULT_BACKEND_URL = "https://account-lifecycle-backend.onrender.com/api/v1"


@dataclass(frozen=True)
class AgentConfig:
    agent_name: str
    agent_secret: str
    backend_url: str
    poll_interval: float
    profile_root: Path
    headless: bool
    provider: str
    heartbeat_interval: float = 30.0
    manual_login_timeout_seconds: float = 900.0


def load_config() -> AgentConfig:
    import yaml

    if not CONFIG_PATH.exists():
        create_config_interactively()
    data = yaml.safe_load(CONFIG_PATH.read_text()) or {}
    return AgentConfig(
        agent_name=str(data.get("agent_name") or data.get("worker_id") or "automation-agent"),
        agent_secret=str(data.get("agent_secret") or data.get("worker_secret") or ""),
        backend_url=str(data.get("backend_url") or DEFAULT_BACKEND_URL),
        poll_interval=float(data.get("poll_interval") or 5),
        profile_root=(AGENT_ROOT / str(data.get("profile_root") or "../storage")).resolve(),
        headless=bool(data.get("headless", False)),
        provider=str(data.get("provider") or "reddit"),
        heartbeat_interval=float(data.get("heartbeat_interval") or 30),
        manual_login_timeout_seconds=float(data.get("manual_login_timeout_seconds") or 900),
    )


def create_config_interactively() -> None:
    """Prompt for first-run agent settings and write agent.yaml."""
    print("agent.yaml was not found. Let's configure this Automation Agent.")
    backend_url = _prompt("Backend URL", DEFAULT_BACKEND_URL)
    agent_name = _prompt("Agent Name", "automation-agent")
    agent_secret = getpass("Agent Secret: ").strip()
    if not agent_secret:
        raise SystemExit("Agent Secret is required. Ask the platform administrator for the secret.")

    content = "\n".join(
        [
            f"agent_name: {agent_name}",
            f"agent_secret: {agent_secret}",
            f"backend_url: {backend_url}",
            "poll_interval: 5",
            "heartbeat_interval: 30",
            "manual_login_timeout_seconds: 900",
            "profile_root: ../storage",
            "headless: false",
            "provider: reddit",
            "",
        ]
    )
    CONFIG_PATH.write_text(content)
    print(f"Created {CONFIG_PATH}")


def _prompt(label: str, default: str) -> str:
    value = input(f"{label} [{default}]: ").strip()
    return value or default
