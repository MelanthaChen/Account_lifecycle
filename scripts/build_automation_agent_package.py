from __future__ import annotations

import shutil
import stat
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_AGENT = ROOT / "automation-agent"
PACKAGE_TEMPLATE = ROOT / "packaging" / "Automation-Agent"
DIST_ROOT = ROOT / "dist"
DIST_PACKAGE = DIST_ROOT / "Automation-Agent"
ZIP_BASE = DIST_ROOT / "Automation-Agent"

EXCLUDED_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "storage",
    "logs",
}
EXCLUDED_FILES = {
    "Install.command",
    "Run.command",
    "agent.yaml",
}


def main() -> None:
    if DIST_PACKAGE.exists():
        shutil.rmtree(DIST_PACKAGE)
    DIST_PACKAGE.mkdir(parents=True)

    copy_package_shell()
    copy_agent_source()
    ensure_executable(DIST_PACKAGE / "Install.command")
    ensure_executable(DIST_PACKAGE / "Run.command")
    (DIST_PACKAGE / "logs").mkdir(exist_ok=True)
    (DIST_PACKAGE / "logs" / ".gitkeep").touch()
    zip_path = shutil.make_archive(str(ZIP_BASE), "zip", root_dir=DIST_ROOT, base_dir="Automation-Agent")
    print(f"Created {DIST_PACKAGE}")
    print(f"Created {zip_path}")


def copy_package_shell() -> None:
    for item in PACKAGE_TEMPLATE.iterdir():
        if item.name == "automation-agent":
            continue
        target = DIST_PACKAGE / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)


def copy_agent_source() -> None:
    shutil.copytree(
        SOURCE_AGENT,
        DIST_PACKAGE / "automation-agent",
        ignore=ignore_agent_files,
    )


def ignore_agent_files(directory: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    for name in names:
        path = Path(directory) / name
        if path.is_dir() and name in EXCLUDED_DIRS:
            ignored.add(name)
        if path.is_file() and name in EXCLUDED_FILES:
            ignored.add(name)
    return ignored


def ensure_executable(path: Path) -> None:
    mode = path.stat().st_mode
    path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


if __name__ == "__main__":
    main()
