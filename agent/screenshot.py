from __future__ import annotations

import io
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from PIL import Image, ImageGrab

from agent.automation import active_window_title


@dataclass
class ScreenshotResult:
    allowed: bool
    image_path: Path | None
    reason: str | None
    screenshot_id: str


def capture_screenshot(
    output_dir: Path,
    allowed_windows: list[str],
    mode: Literal["full", "active"] = "full",
) -> ScreenshotResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    screenshot_id = str(uuid.uuid4())
    title = active_window_title()
    if allowed_windows and not any(window in title for window in allowed_windows):
        return ScreenshotResult(False, None, "capture blocked: active window not allowlisted", screenshot_id)

    image = ImageGrab.grab()

    path = output_dir / f"screenshot-{screenshot_id}.png"
    image.save(path)
    return ScreenshotResult(True, path, None, screenshot_id)


def image_bytes(path: Path, fmt: str = "PNG") -> bytes:
    with path.open("rb") as handle:
        data = handle.read()
    if fmt.upper() == "JPEG":
        image = Image.open(io.BytesIO(data))
        buf = io.BytesIO()
        image.convert("RGB").save(buf, format="JPEG", quality=85)
        return buf.getvalue()
    return data
