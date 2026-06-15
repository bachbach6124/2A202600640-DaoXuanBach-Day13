from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

import httpx

COMMANDS = [
    [sys.executable, "scripts/evaluate_quality.py"],
    [sys.executable, "scripts/benchmark_cost.py"],
    [sys.executable, "scripts/verify_p0.py"],
    [sys.executable, "scripts/validate_logs.py"],
    [sys.executable, "scripts/validate_audit.py"],
]


def wait_for_app() -> None:
    for _ in range(40):
        try:
            if httpx.get("http://127.0.0.1:8000/health", timeout=1).status_code == 200:
                return
        except httpx.HTTPError:
            time.sleep(0.25)
    raise RuntimeError("App did not become healthy")


def main() -> None:
    Path("data/logs.jsonl").unlink(missing_ok=True)
    Path("data/audit.jsonl").unlink(missing_ok=True)
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8000"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        wait_for_app()
        for command in COMMANDS:
            subprocess.run(command, check=True)
    finally:
        server.terminate()
        server.wait(timeout=10)
    print("P0, P1 and P2 verification completed successfully.")


if __name__ == "__main__":
    main()
