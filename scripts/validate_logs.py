from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

LOG_PATH = Path("data/logs.jsonl")
SCHEMA_PATH = Path("config/logging_schema.json")
ENRICHMENT_FIELDS = {"user_id_hash", "session_id", "feature", "model", "env"}
PII_CHECKS = {
    "email": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    "phone_vn": re.compile(r"(?<!\d)(?:\+84|0)(?:[ .-]?\d){9,10}(?!\d)"),
    "cccd": re.compile(r"\b\d{12}\b"),
    "credit_card": re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b"),
    "passport": re.compile(r"\b[A-Z]\d{7,8}\b"),
}


def load_records() -> tuple[list[dict], int]:
    records = []
    invalid_json = 0
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            invalid_json += 1
    return records, invalid_json


def main() -> None:
    if not LOG_PATH.exists():
        print(f"Error: {LOG_PATH} not found. Run the app and send some requests first.")
        sys.exit(1)

    records, invalid_json = load_records()
    if not records:
        print("Error: No valid JSON logs found in data/logs.jsonl")
        sys.exit(1)

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    schema_errors = []
    missing_enrichment = []
    pii_hits = []
    correlation_ids = set()

    for index, record in enumerate(records, start=1):
        errors = sorted(validator.iter_errors(record), key=lambda error: list(error.path))
        if errors:
            schema_errors.append((index, errors[0].message))

        if record.get("service") == "api":
            missing = ENRICHMENT_FIELDS - record.keys()
            if missing:
                missing_enrichment.append((index, sorted(missing)))

        raw = json.dumps(record, ensure_ascii=False)
        for name, pattern in PII_CHECKS.items():
            if pattern.search(raw):
                pii_hits.append((index, record.get("event", "unknown"), name))

        correlation_id = record.get("correlation_id")
        if correlation_id and correlation_id not in {"MISSING", "system"}:
            correlation_ids.add(correlation_id)

    print("--- Lab Verification Results ---")
    print(f"Total log records analyzed: {len(records)}")
    print(f"Invalid JSON lines: {invalid_json}")
    print(f"Records failing JSON schema: {len(schema_errors)}")
    print(f"API records missing enrichment: {len(missing_enrichment)}")
    print(f"Unique request correlation IDs: {len(correlation_ids)}")
    print(f"Potential PII leaks detected: {len(pii_hits)}")
    if schema_errors:
        print(f"  First schema error: line {schema_errors[0][0]}: {schema_errors[0][1]}")
    if missing_enrichment:
        print(f"  First enrichment error: line {missing_enrichment[0][0]}: {missing_enrichment[0][1]}")
    if pii_hits:
        print(f"  First PII hit: line {pii_hits[0][0]} event={pii_hits[0][1]} type={pii_hits[0][2]}")

    score = 100
    schema_failed = invalid_json > 0 or bool(schema_errors)
    if schema_failed:
        score -= 30
    if len(correlation_ids) < 2:
        score -= 20
    if missing_enrichment:
        score -= 20
    if pii_hits:
        score -= 30

    print("\n--- Grading Scorecard ---")
    print(("- [FAILED]" if schema_failed else "+ [PASSED]") + " JSON schema")
    print(
        ("- [FAILED]" if len(correlation_ids) < 2 else "+ [PASSED]")
        + " Correlation ID propagation"
    )
    print(
        ("- [FAILED]" if missing_enrichment else "+ [PASSED]")
        + " Log enrichment"
    )
    print(("- [FAILED]" if pii_hits else "+ [PASSED]") + " PII scrubbing")
    print(f"\nEstimated Score: {max(0, score)}/100")
    sys.exit(0 if score >= 80 else 1)


if __name__ == "__main__":
    main()
