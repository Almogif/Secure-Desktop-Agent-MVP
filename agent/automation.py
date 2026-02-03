from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import pyautogui
from pywinauto import Desktop
import subprocess


@dataclass
class ClickTarget:
    window_title: str
    target: dict[str, str]


def open_app(command: list[str]) -> None:
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.2
    subprocess.Popen(command, close_fds=True)


def type_text(text: str) -> None:
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
    pyautogui.write(text, interval=0.01)


def click_ui_target(target: ClickTarget, timeout_s: int = 10) -> bool:
    desktop = Desktop(backend="uia")
    end_time = time.time() + timeout_s
    while time.time() < end_time:
        try:
            window = desktop.window(title_re=target.window_title)
            window.wait("ready", timeout=2)
            element = window.child_window(**target.target)
            element.wait("enabled", timeout=2)
            element.click_input()
            return True
        except Exception:
            time.sleep(0.5)
    return False


def click_coordinates(x: int, y: int) -> None:
    pyautogui.FAILSAFE = True
    pyautogui.click(x=x, y=y)


def active_window_title() -> str:
    desktop = Desktop(backend="uia")
    window = desktop.get_active()
    return window.window_text()


def to_uia_target(target: dict[str, Any]) -> dict[str, str]:
    by = target.get("by")
    value = target.get("value")
    if by == "automation_id":
        return {"automation_id": value}
    if by == "name":
        return {"title": value}
    if by == "class_name":
        return {"class_name": value}
    raise ValueError("Unsupported target selector")
