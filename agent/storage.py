from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


class JsonStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        if not self.path.exists():
            self._write({})

    def _read(self) -> dict[str, Any]:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    def _write(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def get(self, key: str, default: Any = None) -> Any:
        return self._read().get(key, default)

    def set(self, key: str, value: Any) -> None:
        data = self._read()
        data[key] = value
        self._write(data)


class ReplayCache:
    def __init__(self, store: JsonStore, ttl_seconds: int = 3600) -> None:
        self.store = store
        self.ttl_seconds = ttl_seconds

    def _prune(self, data: dict[str, float], now: float) -> dict[str, float]:
        return {req_id: ts for req_id, ts in data.items() if now - ts <= self.ttl_seconds}

    def seen(self, request_id: str, now: float | None = None) -> bool:
        timestamp = now if now is not None else time.time()
        data = self.store.get("seen_request_ids", {})
        pruned = self._prune(data, timestamp)
        if request_id in pruned:
            return True
        pruned[request_id] = timestamp
        self.store.set("seen_request_ids", pruned)
        return False


class UpdateTracker:
    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def get_last_update_id(self) -> int:
        return int(self.store.get("last_update_id", 0))

    def set_last_update_id(self, update_id: int) -> None:
        self.store.set("last_update_id", update_id)
