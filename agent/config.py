from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("AGENT_DATA_DIR", BASE_DIR / ".agent_data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

SCHEMA_PATH = BASE_DIR / "schemas" / "command.schema.json"
WORKFLOW_DIR = BASE_DIR / "workflows"

DEFAULT_ALLOWED_APPS = {
    "notepad": {
        "command": ["notepad.exe"],
        "description": "Windows Notepad",
    },
    "calc": {
        "command": ["calc.exe"],
        "description": "Windows Calculator",
    },
    "chrome": {
        "command": ["chrome.exe"],
        "description": "Google Chrome",
    },
    "outlook": {
        "command": ["outlook.exe"],
        "description": "Microsoft Outlook",
    },
}

DEFAULT_ALLOWED_WINDOWS = ["Notepad", "Calculator", "Google Chrome", "Outlook"]

DEFAULT_SAFE_REGIONS = [
    {
        "name": "notepad_text_area",
        "x_min": 0,
        "x_max": 1200,
        "y_min": 0,
        "y_max": 900,
    }
]


@dataclass(frozen=True)
class AgentConfig:
    telegram_token: str
    allowed_user_ids: list[int]
    poll_interval_s: float
    rate_limit_per_minute: int
    max_text_length: int
    max_workflow_steps: int
    workflow_timeout_s: int
    allowed_apps: dict[str, dict[str, Any]]
    allowed_windows: list[str]
    safe_regions: list[dict[str, int]]


def load_config() -> AgentConfig:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    allowed_ids_raw = os.environ.get("ALLOWED_TELEGRAM_USER_IDS", "").strip()
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required")
    if not allowed_ids_raw:
        raise RuntimeError("ALLOWED_TELEGRAM_USER_IDS is required")

    allowed_ids = [int(value) for value in allowed_ids_raw.split(",") if value.strip()]

    config_path = Path(os.environ.get("AGENT_CONFIG_PATH", ""))
    overrides: dict[str, Any] = {}
    if config_path.is_file():
        overrides = json.loads(config_path.read_text(encoding="utf-8"))

    return AgentConfig(
        telegram_token=token,
        allowed_user_ids=overrides.get("allowed_user_ids", allowed_ids),
        poll_interval_s=float(overrides.get("poll_interval_s", 2.0)),
        rate_limit_per_minute=int(overrides.get("rate_limit_per_minute", 10)),
        max_text_length=int(overrides.get("max_text_length", 500)),
        max_workflow_steps=int(overrides.get("max_workflow_steps", 20)),
        workflow_timeout_s=int(overrides.get("workflow_timeout_s", 120)),
        allowed_apps=overrides.get("allowed_apps", DEFAULT_ALLOWED_APPS),
        allowed_windows=overrides.get("allowed_windows", DEFAULT_ALLOWED_WINDOWS),
        safe_regions=overrides.get("safe_regions", DEFAULT_SAFE_REGIONS),
    )
