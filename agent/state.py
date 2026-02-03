from __future__ import annotations

import threading
from dataclasses import dataclass
from pathlib import Path

from agent.storage import JsonStore


@dataclass
class AgentState:
    mode: str


class StateManager:
    def __init__(self, store: JsonStore) -> None:
        self.store = store
        self._lock = threading.Lock()

    def get_mode(self) -> str:
        with self._lock:
            return self.store.get("mode", "SAFE")

    def set_mode(self, mode: str) -> None:
        if mode not in {"SAFE", "ARMED"}:
            raise ValueError("Invalid mode")
        with self._lock:
            self.store.set("mode", mode)


def state_store(path: Path) -> JsonStore:
    return JsonStore(path)
