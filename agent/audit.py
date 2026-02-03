from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class AuditEvent:
    timestamp: str
    user_id: int
    request_id: str
    command: str
    params: dict[str, Any]
    result: str
    error: str | None
    screenshot_ids: list[str]


def redact_params(params: dict[str, Any]) -> dict[str, Any]:
    redacted = dict(params)
    if "text" in redacted:
        redacted["text"] = "<redacted>"
    return redacted


class AuditLogger:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, event: AuditEvent) -> None:
        line = json.dumps(asdict(event), ensure_ascii=False)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
