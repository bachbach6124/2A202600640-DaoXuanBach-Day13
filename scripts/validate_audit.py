from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

AUDIT_PATH = Path("data/audit.jsonl")
SCHEMA_PATH = Path("config/audit_schema.json")
PII = re.compile(
    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b|"
    r"(?<!\d)(?:\+84|0)(?:[ .-]?\d){9,10}(?!\d)|"
    r"\b\d{12}\b|\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    re.IGNORECASE,
)


def main() -> None:
    if not AUDIT_PATH.exists():
        print(f"Error: {AUDIT_PATH} not found")
        raise SystemExit(1)
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    records = []
    errors = []
    pii_hits = []
    for index, line in enumerate(
        AUDIT_PATH.read_text(encoding="utf-8").splitlines(), start=1
    ):
        try:
            record = json.loads(line)
            records.append(record)
            errors.extend(
                f"line {index}: {error.message}"
                for error in validator.iter_errors(record)
            )
            if PII.search(line):
                pii_hits.append(index)
        except json.JSONDecodeError as exc:
            errors.append(f"line {index}: {exc}")
    print(f"Audit records: {len(records)}")
    print(f"Schema errors: {len(errors)}")
    print(f"PII leaks: {len(pii_hits)}")
    if errors:
        print(errors[0])
    sys.exit(0 if records and not errors and not pii_hits else 1)


if __name__ == "__main__":
    main()
