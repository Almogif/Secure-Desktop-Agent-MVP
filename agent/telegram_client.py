from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any

import requests


@dataclass
class TelegramMessage:
    update_id: int
    message_id: int
    user_id: int
    text: str


class TelegramClient:
    def __init__(self, token: str) -> None:
        self.base_url = f"https://api.telegram.org/bot{token}"

    def get_updates(self, offset: int | None = None, timeout: int = 30) -> list[TelegramMessage]:
        params: dict[str, Any] = {"timeout": timeout}
        if offset is not None:
            params["offset"] = offset
        response = requests.get(f"{self.base_url}/getUpdates", params=params, timeout=timeout + 5)
        response.raise_for_status()
        data = response.json()
        if not data.get("ok"):
            raise RuntimeError("Telegram getUpdates failed")
        messages: list[TelegramMessage] = []
        for item in data.get("result", []):
            message = item.get("message")
            if not message or "text" not in message:
                continue
            user = message.get("from", {})
            messages.append(
                TelegramMessage(
                    update_id=item["update_id"],
                    message_id=message["message_id"],
                    user_id=user.get("id", 0),
                    text=message.get("text", ""),
                )
            )
        return messages

    def send_message(self, chat_id: int, text: str) -> None:
        payload = {"chat_id": chat_id, "text": text}
        response = requests.post(f"{self.base_url}/sendMessage", data=payload, timeout=20)
        response.raise_for_status()

    def send_document(self, chat_id: int, filename: str, data: bytes) -> None:
        files = {"document": (filename, data)}
        payload = {"chat_id": chat_id}
        response = requests.post(f"{self.base_url}/sendDocument", data=payload, files=files, timeout=30)
        response.raise_for_status()

    def send_photo(self, chat_id: int, filename: str, data: bytes) -> None:
        files = {"photo": (filename, data)}
        payload = {"chat_id": chat_id}
        response = requests.post(f"{self.base_url}/sendPhoto", data=payload, files=files, timeout=30)
        response.raise_for_status()


def backoff_sleep(attempt: int) -> None:
    delay = min(10, 1 + attempt)
    time.sleep(delay)
