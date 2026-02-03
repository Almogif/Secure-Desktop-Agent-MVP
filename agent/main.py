from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


import keyboard

from agent.audit import AuditLogger
from agent.config import DATA_DIR, SCHEMA_PATH, WORKFLOW_DIR, load_config
from agent.handler import CommandHandler
from agent.schema import SchemaValidator
from agent.security import AllowList, RateLimiter
from agent.state import StateManager
from agent.storage import JsonStore, ReplayCache, UpdateTracker
from agent.telegram_client import TelegramClient, backoff_sleep
from agent.workflow import WorkflowLoader, WorkflowRunner


def build_handler() -> CommandHandler:
    config = load_config()
    schema = SchemaValidator(SCHEMA_PATH)
    workflow_loader = WorkflowLoader(WORKFLOW_DIR)
    allowlist = AllowList(config.allowed_apps, workflow_loader.available_workflows())
    replay_cache = ReplayCache(JsonStore(DATA_DIR / "replay_cache.json"))
    rate_limiter = RateLimiter(config.rate_limit_per_minute)
    state_manager = StateManager(JsonStore(DATA_DIR / "state.json"))
    audit_logger = AuditLogger(DATA_DIR / "audit.jsonl")
    workflow_runner = WorkflowRunner(config.max_workflow_steps, config.workflow_timeout_s)
    screenshot_dir = DATA_DIR / "screenshots"
    return CommandHandler(
        config=config,
        schema_validator=schema,
        allowlist=allowlist,
        replay_cache=replay_cache,
        rate_limiter=rate_limiter,
        state_manager=state_manager,
        workflow_loader=workflow_loader,
        workflow_runner=workflow_runner,
        audit_logger=audit_logger,
        screenshot_dir=screenshot_dir,
    )


def install_kill_switch(state_manager: StateManager) -> None:
    def toggle_safe() -> None:
        current = state_manager.get_mode()
        state_manager.set_mode("SAFE")
        if current != "SAFE":
            return
        state_manager.set_mode("ARMED")

    keyboard.add_hotkey("ctrl+alt+s", toggle_safe)


def run_agent() -> None:
    config = load_config()
    telegram = TelegramClient(config.telegram_token)
    handler = build_handler()
    update_tracker = UpdateTracker(JsonStore(DATA_DIR / "updates.json"))

    state_manager = StateManager(JsonStore(DATA_DIR / "state.json"))
    install_kill_switch(state_manager)

    last_update_id = update_tracker.get_last_update_id()
    failure_count = 0

    while True:
        try:
            updates = telegram.get_updates(offset=last_update_id + 1 if last_update_id else None)
            for message in updates:
                last_update_id = max(last_update_id, message.update_id)
                update_tracker.set_last_update_id(last_update_id)
                if message.user_id not in config.allowed_user_ids:
                    continue
                handler.handle({"text": message.text}, message.user_id, telegram)
            failure_count = 0
            time.sleep(config.poll_interval_s)
        except Exception:
            failure_count += 1
            if failure_count >= 3:
                state_manager.set_mode("SAFE")
            backoff_sleep(failure_count)


def set_mode(mode: str) -> None:
    state_manager = StateManager(JsonStore(DATA_DIR / "state.json"))
    state_manager.set_mode(mode)
    print(f"Mode set to {mode}")


def test_screenshot() -> None:
    from agent.screenshot import capture_screenshot

    config = load_config()
    result = capture_screenshot(DATA_DIR / "screenshots", config.allowed_windows)
    print(json.dumps({"allowed": result.allowed, "path": str(result.image_path)}))


def main() -> None:
    parser = argparse.ArgumentParser(description="Secure desktop agent")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("run")
    sub.add_parser("arm")
    sub.add_parser("safe")
    sub.add_parser("test_screenshot")
    args = parser.parse_args()

    if args.command == "run":
        run_agent()
    elif args.command == "arm":
        set_mode("ARMED")
    elif args.command == "safe":
        set_mode("SAFE")
    elif args.command == "test_screenshot":
        test_screenshot()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
