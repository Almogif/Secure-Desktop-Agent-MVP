from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator


class SchemaValidator:
    def __init__(self, schema_path: Path) -> None:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        self.validator = Draft7Validator(schema)

    def validate(self, payload: dict[str, Any]) -> list[str]:
        errors = []
        for error in sorted(self.validator.iter_errors(payload), key=str):
            errors.append(error.message)
        return errors
