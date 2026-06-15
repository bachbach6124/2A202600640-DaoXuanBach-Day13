from __future__ import annotations

import re
import time
from dataclasses import dataclass

from structlog.contextvars import get_contextvars

from . import metrics
from .mock_llm import FakeLLM
from .mock_rag import retrieve
from .pii import summarize_text
from .tracing import (
    current_trace_id,
    observe,
    trace_context,
    update_current_observation,
    update_current_trace,
)


@dataclass
class AgentResult:
    answer: str
    latency_ms: int
    tokens_in: int
    tokens_out: int
    cost_usd: float
    quality_score: float
    trace_id: str | None


class LabAgent:
    def __init__(self, model: str = "claude-sonnet-4-5") -> None:
        self.model = model
        self.llm = FakeLLM(model=model)

    def run(self, user_id_hash: str, feature: str, session_id: str, message: str) -> AgentResult:
        metadata = {
            "feature": feature,
            "model": self.model,
            "correlation_id": get_contextvars().get("correlation_id"),
        }
        with trace_context(
            user_id=user_id_hash,
            session_id=session_id,
            tags=["lab", feature, self.model],
            metadata=metadata,
        ):
            return self._run_traced(
                user_id_hash=user_id_hash,
                feature=feature,
                session_id=session_id,
                message=message,
            )

    @observe(name="agent-run", capture_input=False, capture_output=False)
    def _run_traced(
        self,
        user_id_hash: str,
        feature: str,
        session_id: str,
        message: str,
    ) -> AgentResult:
        started = time.perf_counter()
        trace_metadata = {
            "feature": feature,
            "model": self.model,
            "correlation_id": get_contextvars().get("correlation_id"),
        }
        update_current_trace(
            user_id=user_id_hash,
            session_id=session_id,
            tags=["lab", feature, self.model],
            metadata=trace_metadata,
        )

        docs = retrieve(message)
        prompt = f"Feature={feature}\nDocs={docs}\nQuestion={message}"
        response = self.llm.generate(prompt)
        quality_score = self._heuristic_quality(message, response.text, docs)
        latency_ms = int((time.perf_counter() - started) * 1000)
        cost_usd = self._estimate_cost(
            response.usage.input_tokens,
            response.usage.output_tokens,
        )
        trace_id = current_trace_id()

        update_current_observation(
            metadata={
                **trace_metadata,
                "doc_count": len(docs),
                "latency_ms": latency_ms,
                "query_preview": summarize_text(message),
                "quality_score": quality_score,
                "cost_usd": cost_usd,
            },
            output={"answer_preview": summarize_text(response.text)},
        )
        metrics.record_request(
            latency_ms=latency_ms,
            cost_usd=cost_usd,
            tokens_in=response.usage.input_tokens,
            tokens_out=response.usage.output_tokens,
            quality_score=quality_score,
            trace_id=trace_id,
        )

        return AgentResult(
            answer=response.text,
            latency_ms=latency_ms,
            tokens_in=response.usage.input_tokens,
            tokens_out=response.usage.output_tokens,
            cost_usd=cost_usd,
            quality_score=quality_score,
            trace_id=trace_id,
        )

    def _estimate_cost(self, tokens_in: int, tokens_out: int) -> float:
        input_cost = (tokens_in / 1_000_000) * 3
        output_cost = (tokens_out / 1_000_000) * 15
        return round(input_cost + output_cost, 6)

    def _heuristic_quality(self, question: str, answer: str, docs: list[str]) -> float:
        if not docs or "No domain document matched" in docs[0]:
            return 0.35
        meaningful = {
            token
            for token in re.findall(r"[a-z0-9]+", " ".join(docs).lower())
            if len(token) >= 4
        }
        answer_tokens = set(re.findall(r"[a-z0-9]+", answer.lower()))
        grounding = len(meaningful & answer_tokens) / max(1, len(meaningful))
        score = 0.55 + (0.4 * grounding)
        if len(answer) <= 180:
            score += 0.05
        if "[REDACTED" in answer:
            score -= 0.2
        return round(max(0.0, min(1.0, score)), 2)
