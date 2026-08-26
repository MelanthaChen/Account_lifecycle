from __future__ import annotations

from dataclasses import dataclass
from os import environ
from pathlib import Path

AGENT_ROOT = Path(__file__).resolve().parent
CONFIG_PATH = Path(environ.get("AGENT_CONFIG_PATH", AGENT_ROOT / "agent.yaml")).expanduser().resolve()
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
        raise SystemExit(_missing_config_message())
    data = yaml.safe_load(CONFIG_PATH.read_text()) or {}
    if _has_invalid_config(data):
        raise SystemExit(_invalid_config_message())
    return AgentConfig(
        agent_name=str(data.get("agent_name") or data.get("worker_id") or "automation-agent"),
        agent_secret=str(data.get("agent_secret") or data.get("worker_secret") or ""),
        backend_url=str(data.get("backend_url") or DEFAULT_BACKEND_URL),
        poll_interval=float(data.get("poll_interval") or 5),
        profile_root=_resolve_config_path(str(data.get("profile_root") or "../storage")),
        headless=bool(data.get("headless", False)),
        provider=str(data.get("provider") or "reddit"),
        heartbeat_interval=float(data.get("heartbeat_interval") or 30),
        manual_login_timeout_seconds=float(data.get("manual_login_timeout_seconds") or 900),
    )


def _has_invalid_config(data: dict) -> bool:
    secret = str(data.get("agent_secret") or data.get("worker_secret") or "").strip()
    backend_url = str(data.get("backend_url") or "").strip()
    template_values = {
        "",
        "replace-with-render-agent-secret",
        "replace-with-agent-secret",
        "your-agent-secret",
    }
    return (
        secret in template_values
        or not backend_url
        or "your-render-backend" in backend_url
        or backend_url == "https://your-render-backend.onrender.com/api/v1"
    )


def _missing_config_message() -> str:
    return (
        "\nMissing configuration.\n\n"
        "This dedicated Automation Agent package should include agent.yaml.\n"
        "Please re-download the complete package or contact the project owner.\n"
    )


def _invalid_config_message() -> str:
    return (
        "\nInvalid Automation Agent configuration.\n\n"
        "This dedicated package is expected to ship with backend_url, agent_name, and agent_secret already filled in.\n"
        "Please re-download the complete package or contact the project owner.\n"
    )


def _resolve_config_path(value: str) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return (CONFIG_PATH.parent / path).resolve()
