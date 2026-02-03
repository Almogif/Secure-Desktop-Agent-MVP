from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agent.audit import AuditEvent, AuditLogger, now_iso, redact_params
from agent.automation import ClickTarget, click_coordinates, click_ui_target, open_app, type_text, to_uia_target
from agent.config import AgentConfig
from agent.schema import SchemaValidator
from agent.screenshot import ScreenshotResult, capture_screenshot, image_bytes
from agent.security import AllowList, RateLimiter
from agent.state import StateManager
from agent.storage import ReplayCache
from agent.telegram_client import TelegramClient
from agent.workflow import WorkflowLoader, WorkflowRunner


@dataclass
class CommandResult:
    status: str
    message: str
    screenshot_ids: list[str]


class CommandHandler:
    def __init__(
        self,
        config: AgentConfig,
        schema_validator: SchemaValidator,
        allowlist: AllowList,
        replay_cache: ReplayCache,
        rate_limiter: RateLimiter,
        state_manager: StateManager,
        workflow_loader: WorkflowLoader,
        workflow_runner: WorkflowRunner,
        audit_logger: AuditLogger,
        screenshot_dir: Path,
    ) -> None:
        self.config = config
        self.schema_validator = schema_validator
        self.allowlist = allowlist
        self.replay_cache = replay_cache
        self.rate_limiter = rate_limiter
        self.state_manager = state_manager
        self.workflow_loader = workflow_loader
        self.workflow_runner = workflow_runner
        self.audit_logger = audit_logger
        self.screenshot_dir = screenshot_dir

    def handle(self, message: dict[str, Any], user_id: int, telegram: TelegramClient) -> None:
        rate_result = self.rate_limiter.allow(user_id)
        if not rate_result.allowed:
            telegram.send_message(user_id, f"Rate limit exceeded. Retry after {rate_result.retry_after_s}s")
            return

        try:
            payload = json.loads(message["text"])
        except json.JSONDecodeError:
            telegram.send_message(user_id, "Invalid JSON. Example: {\"request_id\":\"uuid\",\"command\":\"screenshot\",\"params\":{\"mode\":\"full\"}}")
            return

        errors = self.schema_validator.validate(payload)
        if errors:
            telegram.send_message(user_id, f"Schema validation failed: {errors[0]}")
            return

        request_id = payload.get("request_id") or str(uuid.uuid4())
        if self.replay_cache.seen(request_id):
            telegram.send_message(user_id, "Replay detected: request_id already processed")
            return

        if self.state_manager.get_mode() == "SAFE" and payload["command"] not in {"screenshot", "status", "help"}:
            telegram.send_message(user_id, "Agent is in SAFE mode. Only screenshot/status/help allowed.")
            return

        result = self.execute_command(payload, user_id, telegram)
        self.audit_logger.log(
            AuditEvent(
                timestamp=now_iso(),
                user_id=user_id,
                request_id=request_id,
                command=payload["command"],
                params=redact_params(payload.get("params", {})),
                result=result.status,
                error=None if result.status == "ok" else result.message,
                screenshot_ids=result.screenshot_ids,
            )
        )

    def execute_command(self, payload: dict[str, Any], user_id: int, telegram: TelegramClient) -> CommandResult:
        command = payload["command"]
        params = payload.get("params", {})
        screenshots: list[str] = []

        before = self._take_screenshot(telegram, user_id, "before")
        if before:
            screenshots.append(before)

        if command == "help":
            telegram.send_message(user_id, "Commands: screenshot, open_app, type_text, click, run_workflow, status, help")
            return CommandResult("ok", "help returned", screenshots)

        if command == "status":
            telegram.send_message(user_id, f"Mode: {self.state_manager.get_mode()}")
            return CommandResult("ok", "status returned", screenshots)

        try:
            if command == "screenshot":
                mode = params.get("mode", "full")
                return self._send_screenshot(telegram, user_id, "manual", screenshots, mode)
            if command == "open_app":
                app_id = params.get("app_id", "")
                if not self.allowlist.validate_app(app_id):
                    raise ValueError("app_id not allowlisted")
                open_app(self.config.allowed_apps[app_id]["command"])
            elif command == "type_text":
                text = params.get("text", "")
                if not self.allowlist.validate_text(text, self.config.max_text_length):
                    raise ValueError("text length invalid")
                type_text(text)
            elif command == "click":
                if "target" in params:
                    target = ClickTarget(
                        window_title=params.get("window_title", ""),
                        target=to_uia_target(params["target"]),
                    )
                    if not click_ui_target(target):
                        raise RuntimeError("UI element not found")
                elif "coordinates" in params:
                    coords = params["coordinates"]
                    x = int(coords.get("x", -1))
                    y = int(coords.get("y", -1))
                    if not self.allowlist.validate_coordinates(x, y):
                        raise ValueError("coordinates invalid")
                    if not coords.get("confirmed"):
                        raise ValueError("coordinate click requires confirmed=true")
                    click_coordinates(x, y)
                else:
                    raise ValueError("click requires target or coordinates")
            elif command == "run_workflow":
                workflow_id = params.get("workflow_id", "")
                if not self.allowlist.validate_workflow(workflow_id):
                    raise ValueError("workflow_id not allowlisted")
                return self._run_workflow(workflow_id, telegram, user_id, screenshots)
            else:
                raise ValueError("command not allowlisted")
        except Exception as exc:
            error_result = self._send_screenshot(telegram, user_id, f"error: {exc}", screenshots)
            return CommandResult("error", str(exc), error_result.screenshot_ids)

        after = self._take_screenshot(telegram, user_id, "after")
        if after:
            screenshots.append(after)
        telegram.send_message(user_id, f"Command {command} completed")
        return CommandResult("ok", "completed", screenshots)

    def _run_workflow(self, workflow_id: str, telegram: TelegramClient, user_id: int, screenshots: list[str]) -> CommandResult:
        workflow = self.workflow_loader.load(workflow_id)
        start = time.time()
        for index, step in enumerate(workflow.steps, start=1):
            if not self.workflow_runner.should_continue(index, start):
                return CommandResult("error", "workflow timeout or max steps exceeded", screenshots)
            step_payload = {
                "command": step.get("command"),
                "params": step.get("params", {}),
                "request_id": f"{workflow_id}-{index}",
            }
            errors = self.schema_validator.validate(step_payload)
            if errors:
                return CommandResult("error", f"workflow step invalid: {errors[0]}", screenshots)
            self.execute_command(step_payload, user_id, telegram)
        return CommandResult("ok", "workflow completed", screenshots)

    def _take_screenshot(self, telegram: TelegramClient, user_id: int, label: str) -> str | None:
        result = capture_screenshot(self.screenshot_dir, self.config.allowed_windows)
        if not result.allowed:
            telegram.send_message(user_id, f"Screenshot blocked: {result.reason}")
            return None
        self._send_screenshot_bytes(telegram, user_id, result, label)
        return result.screenshot_id

    def _send_screenshot(
        self,
        telegram: TelegramClient,
        user_id: int,
        label: str,
        screenshots: list[str],
        mode: str = "full",
    ) -> CommandResult:
        result = capture_screenshot(self.screenshot_dir, self.config.allowed_windows, mode=mode)
        if not result.allowed:
            telegram.send_message(user_id, f"Screenshot blocked: {result.reason}")
            return CommandResult("error", result.reason or "blocked", screenshots)
        self._send_screenshot_bytes(telegram, user_id, result, label)
        screenshots.append(result.screenshot_id)
        return CommandResult("ok", "screenshot sent", screenshots)

    def _send_screenshot_bytes(self, telegram: TelegramClient, user_id: int, result: ScreenshotResult, label: str) -> None:
        if not result.image_path:
            return
        data = image_bytes(result.image_path, fmt="PNG")
        telegram.send_document(user_id, f"{label}-{result.image_path.name}", data)
