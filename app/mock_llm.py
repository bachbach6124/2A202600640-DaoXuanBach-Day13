from __future__ import annotations

import random
import time
from dataclasses import dataclass

from .incidents import STATE
from .logging_config import get_logger
from .pii import summarize_text
from .tracing import observe, update_current_observation

log = get_logger()


@dataclass
class FakeUsage:
    input_tokens: int
    output_tokens: int


@dataclass
class FakeResponse:
    text: str
    usage: FakeUsage
    model: str


class FakeLLM:
    def __init__(self, model: str = "claude-sonnet-4-5") -> None:
        self.model = model

    @observe(
        name="llm-generation",
        as_type="generation",
        capture_input=False,
        capture_output=False,
    )
    def generate(self, prompt: str) -> FakeResponse:
        started = time.perf_counter()
        time.sleep(0.15)
        input_tokens = max(20, len(prompt) // 4)
        output_tokens = random.randint(80, 180)
        if STATE["cost_spike"]:
            output_tokens *= 5
        answer = (
            "Starter answer. Teams should improve this output logic and add better quality checks. "
            "Use retrieved context and keep responses concise."
        )
        latency_ms = int((time.perf_counter() - started) * 1000)
        update_current_observation(
            metadata={"latency_ms": latency_ms, "prompt_preview": summarize_text(prompt)},
            usage_details={"input": input_tokens, "output": output_tokens},
            model=self.model,
            output={"answer_preview": summarize_text(answer)},
            generation=True,
        )
        log.info(
            "llm_completed",
            service="agent",
            model=self.model,
            latency_ms=latency_ms,
            tokens_in=input_tokens,
            tokens_out=output_tokens,
            payload={"answer_preview": summarize_text(answer)},
        )
        return FakeResponse(
            text=answer,
            usage=FakeUsage(input_tokens, output_tokens),
            model=self.model,
        )
