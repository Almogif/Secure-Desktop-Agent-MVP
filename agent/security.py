from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


@dataclass
class RateLimitResult:
    allowed: bool
    retry_after_s: int | None


class RateLimiter:
    def __init__(self, limit_per_minute: int) -> None:
        self.limit_per_minute = limit_per_minute
        self.events: dict[int, list[float]] = {}

    def allow(self, user_id: int, now: float | None = None) -> RateLimitResult:
        timestamp = now if now is not None else time.time()
        window_start = timestamp - 60
        history = self.events.get(user_id, [])
        history = [t for t in history if t >= window_start]
        if len(history) >= self.limit_per_minute:
            retry_after = int(history[0] + 60 - timestamp) + 1
            self.events[user_id] = history
            return RateLimitResult(False, max(retry_after, 1))
        history.append(timestamp)
        self.events[user_id] = history
        return RateLimitResult(True, None)


class AllowList:
    def __init__(self, allowed_apps: dict[str, dict[str, Any]], allowed_workflows: set[str]) -> None:
        self.allowed_apps = allowed_apps
        self.allowed_workflows = allowed_workflows

    def validate_app(self, app_id: str) -> bool:
        return app_id in self.allowed_apps

    def validate_workflow(self, workflow_id: str) -> bool:
        return workflow_id in self.allowed_workflows

    def validate_text(self, text: str, max_length: int) -> bool:
        return 0 < len(text) <= max_length

    def validate_coordinates(self, x: int, y: int, max_x: int = 3840, max_y: int = 2160) -> bool:
        return 0 <= x <= max_x and 0 <= y <= max_y
