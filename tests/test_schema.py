from pathlib import Path

from agent.schema import SchemaValidator


def test_valid_screenshot_command():
    schema = SchemaValidator(Path("schemas/command.schema.json"))
    payload = {
        "request_id": "abcd1234",
        "command": "screenshot",
        "params": {"mode": "full"},
    }
    errors = schema.validate(payload)
    assert errors == []


def test_invalid_click_command_missing_target():
    schema = SchemaValidator(Path("schemas/command.schema.json"))
    payload = {
        "request_id": "abcd1234",
        "command": "click",
        "params": {"window_title": "Notepad"},
    }
    errors = schema.validate(payload)
    assert errors
