"""QYIR v1 validator — loads JSON, validates, returns structured result."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
import sys

from pydantic import ValidationError

from qyir.schema import QYIR


@dataclass
class ValidationIssue:
    """A single validation error with location and message."""

    path: str
    message: str


@dataclass
class ValidationResult:
    """Result of QYIR validation."""

    valid: bool = True
    issues: List[ValidationIssue] = field(default_factory=list)

    def add(self, path: str, message: str) -> None:
        self.valid = False
        self.issues.append(ValidationIssue(path=path, message=message))

    @property
    def summary(self) -> str:
        if self.valid:
            return "QYIR validation passed."
        lines = ["QYIR validation failed:"]
        for issue in self.issues:
            lines.append(f"  [{issue.path}] {issue.message}")
        return "\n".join(lines)


def validate_qyir(data: dict) -> ValidationResult:
    """Validate a QYIR dictionary. Returns ValidationResult."""
    result = ValidationResult()

    try:
        QYIR.model_validate(data)
    except ValidationError as e:
        for error in e.errors():
            loc_parts = [str(p) for p in error["loc"] if p != "__root__"]
            path = ".".join(loc_parts) if loc_parts else "root"
            result.add(path, error["msg"])

    return result


def validate_qyir_file(filepath: str | Path) -> ValidationResult:
    """Load a QYIR JSON file and validate it."""
    path = Path(filepath)
    result = ValidationResult()

    if not path.exists():
        result.add("file", f"File not found: {path}")
        return result

    try:
        raw = path.read_text(encoding="utf-8")
    except Exception as e:
        result.add("file", f"Cannot read file: {e}")
        return result

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        result.add("json", f"Invalid JSON: {e}")
        return result

    if not isinstance(data, dict):
        result.add("json", "QYIR root must be a JSON object")
        return result

    # Delegate to dict-based validator
    return validate_qyir(data)


def main(argv: Optional[list[str]] = None) -> int:
    """CLI entry point for `python -m qyir.validator <file>`."""
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        print("Usage: python -m qyir.validator <qyir_file.json>")
        return 2

    result = validate_qyir_file(args[0])
    print(result.summary)
    return 0 if result.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
