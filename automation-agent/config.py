from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

AGENT_ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class AgentConfig:
    worker_id: str
    worker_secret: str
    backend_url: str
    poll_interval: float
    profile_root: Path
    headless: bool
    provider: str
    heartbeat_interval: float = 30.0
    manual_login_timeout_seconds: float = 900.0


def load_config() -> AgentConfig:
    import yaml

    config_path = AGENT_ROOT / "agent.yaml"
    data = yaml.safe_load(config_path.read_text()) or {}
    return AgentConfig(
        worker_id=str(data.get("worker_id") or "local-agent-1"),
        worker_secret=str(data.get("worker_secret") or ""),
        backend_url=str(data.get("backend_url") or "http://127.0.0.1:8001/api/v1"),
        poll_interval=float(data.get("poll_interval") or 5),
        profile_root=(AGENT_ROOT / str(data.get("profile_root") or "../storage")).resolve(),
        headless=bool(data.get("headless", False)),
        provider=str(data.get("provider") or "reddit"),
        heartbeat_interval=float(data.get("heartbeat_interval") or 30),
        manual_login_timeout_seconds=float(data.get("manual_login_timeout_seconds") or 900),
    )
