from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class Workflow:
    workflow_id: str
    steps: list[dict[str, Any]]


class WorkflowLoader:
    def __init__(self, workflow_dir: Path) -> None:
        self.workflow_dir = workflow_dir

    def available_workflows(self) -> set[str]:
        return {path.stem for path in self.workflow_dir.glob("*.json")}

    def load(self, workflow_id: str) -> Workflow:
        path = self.workflow_dir / f"{workflow_id}.json"
        if not path.exists():
            raise FileNotFoundError(f"Workflow {workflow_id} not found")
        data = json.loads(path.read_text(encoding="utf-8"))
        steps = data.get("steps", [])
        return Workflow(workflow_id=workflow_id, steps=steps)


class WorkflowRunner:
    def __init__(self, max_steps: int, timeout_s: int) -> None:
        self.max_steps = max_steps
        self.timeout_s = timeout_s

    def should_continue(self, step_index: int, start_time: float) -> bool:
        if step_index >= self.max_steps:
            return False
        return (time.time() - start_time) <= self.timeout_s
