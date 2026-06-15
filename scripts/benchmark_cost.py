from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from structlog.contextvars import bind_contextvars

from app.agent import LabAgent
from app.mock_llm import estimate_tokens
from app.mock_rag import retrieve
from app.pii import summarize_text

INPUT = Path("data/sample_queries.jsonl")
OUTPUT = Path("docs/evidence/cost-optimization.json")
LEGACY_OUTPUT_TOKENS = 130


def benchmark() -> dict:
    bind_contextvars(correlation_id="offline-cost-benchmark")
    agent = LabAgent()
    rows = []
    for line in INPUT.read_text(encoding="utf-8").splitlines():
        query = json.loads(line)
        docs = retrieve(query["message"])
        prompt = (
            f"Feature={query['feature']}\nDocs={docs}\nQuestion={query['message']}"
        )
        answer = agent.llm._grounded_answer(prompt)
        tokens_in = estimate_tokens(prompt)
        optimized_output = estimate_tokens(answer)
        baseline_cost = agent._estimate_cost(tokens_in, LEGACY_OUTPUT_TOKENS)
        optimized_cost = agent._estimate_cost(tokens_in, optimized_output)
        rows.append(
            {
                "question": summarize_text(query["message"]),
                "baseline_output_tokens": LEGACY_OUTPUT_TOKENS,
                "optimized_output_tokens": optimized_output,
                "baseline_cost_usd": baseline_cost,
                "optimized_cost_usd": optimized_cost,
            }
        )
    baseline_tokens = sum(row["baseline_output_tokens"] for row in rows)
    optimized_tokens = sum(row["optimized_output_tokens"] for row in rows)
    baseline_cost = round(sum(row["baseline_cost_usd"] for row in rows), 6)
    optimized_cost = round(sum(row["optimized_cost_usd"] for row in rows), 6)
    return {
        "methodology": (
            "Baseline uses the previous random output midpoint of 130 tokens/request; "
            "optimized uses deterministic concise grounded answers."
        ),
        "requests": len(rows),
        "before": {"output_tokens": baseline_tokens, "cost_usd": baseline_cost},
        "after": {"output_tokens": optimized_tokens, "cost_usd": optimized_cost},
        "token_reduction_pct": round(
            (baseline_tokens - optimized_tokens) / baseline_tokens * 100, 2
        ),
        "cost_reduction_pct": round(
            (baseline_cost - optimized_cost) / baseline_cost * 100, 2
        ),
        "cases": rows,
    }


def main() -> None:
    report = benchmark()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({key: report[key] for key in report if key != "cases"}, indent=2))
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
