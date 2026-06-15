from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any

from .pii import scrub_value

_LOCK = Lock()


def audit_path() -> Path:
    return Path(os.getenv("AUDIT_LOG_PATH", "data/audit.jsonl"))


def write_audit(
    *,
    actor: str,
    action: str,
    result: str,
    correlation_id: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    record = scrub_value(
        {
            "ts": datetime.now(timezone.utc).isoformat(),
            "actor": actor,
            "action": action,
            "result": result,
            "correlation_id": correlation_id,
            "details": details or {},
        }
    )
    path = audit_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with _LOCK, path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=True) + "\n")
    return record


def recent_audit(limit: int = 20) -> list[dict[str, Any]]:
    path = audit_path()
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records[-limit:]
