from __future__ import annotations

import time

from .incidents import STATE
from .logging_config import get_logger
from .pii import summarize_text
from .tracing import observe, update_current_observation

log = get_logger()

CORPUS = {
    "refund": ["Refunds are available within 7 days with proof of purchase."],
    "monitoring": ["Metrics detect incidents, traces localize them, logs explain root cause."],
    "policy": ["Do not expose PII in logs. Use sanitized summaries only."],
}


@observe(name="rag-retrieval", capture_input=False, capture_output=False)
def retrieve(message: str) -> list[str]:
    started = time.perf_counter()
    if STATE["tool_fail"]:
        log.error(
            "tool_failed",
            service="agent",
            tool_name="mock-rag",
            error_type="RuntimeError",
            payload={"detail": "Vector store timeout"},
        )
        raise RuntimeError("Vector store timeout")
    if STATE["rag_slow"]:
        time.sleep(5.5)
    lowered = message.lower()
    for key, docs in CORPUS.items():
        if key in lowered:
            _record_retrieval(message, docs, started)
            return docs
    docs = ["No domain document matched. Use general fallback answer."]
    _record_retrieval(message, docs, started)
    return docs


def _record_retrieval(message: str, docs: list[str], started: float) -> None:
    latency_ms = int((time.perf_counter() - started) * 1000)
    metadata = {
        "doc_count": len(docs),
        "latency_ms": latency_ms,
        "query_preview": summarize_text(message),
    }
    update_current_observation(metadata=metadata, output={"doc_count": len(docs)})
    log.info(
        "tool_completed",
        service="agent",
        tool_name="mock-rag",
        latency_ms=latency_ms,
        payload=metadata,
    )
