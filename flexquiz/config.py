from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(slots=True)
class AppConfig:
    setup_complete: bool
    workspace_dir: str
    theme: str


def _base_dir() -> Path:
    if os.name == "nt":
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / "FlexQuiz"
    return Path.home() / ".flexquiz"


def config_path() -> Path:
    return _base_dir() / "config.json"


def load_config() -> AppConfig:
    path = config_path()
    if not path.exists():
        return AppConfig(setup_complete=False, workspace_dir=str(Path.home() / "FlexQuizWorkspace"), theme="dark")

    payload = json.loads(path.read_text(encoding="utf-8"))
    return AppConfig(
        setup_complete=bool(payload.get("setup_complete", False)),
        workspace_dir=str(payload.get("workspace_dir", Path.home() / "FlexQuizWorkspace")),
        theme=str(payload.get("theme", "dark")),
    )


def save_config(cfg: AppConfig) -> None:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(cfg), indent=2), encoding="utf-8")


def ensure_workspace(path: str) -> Path:
    workspace = Path(path)
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace
