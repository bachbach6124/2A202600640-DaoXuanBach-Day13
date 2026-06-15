from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from structlog.contextvars import bind_contextvars

from app.agent import LabAgent
from app.mock_rag import retrieve

INPUT = Path("data/expected_answers.jsonl")
OUTPUT = Path("docs/evidence/quality-evaluation.json")


def evaluate() -> dict:
    bind_contextvars(correlation_id="offline-quality-eval")
    agent = LabAgent()
    cases = []
    for line in INPUT.read_text(encoding="utf-8").splitlines():
        expected = json.loads(line)
        docs = retrieve(expected["question"])
        prompt = f"Feature=qa\nDocs={docs}\nQuestion={expected['question']}"
        answer = agent.llm.generate(prompt).text
        found = [
            phrase
            for phrase in expected["must_include"]
            if phrase.lower() in answer.lower()
        ]
        cases.append(
            {
                "question": expected["question"],
                "answer": answer,
                "must_include": expected["must_include"],
                "found": found,
                "passed": len(found) == len(expected["must_include"]),
                "quality_score": agent._heuristic_quality(
                    expected["question"], answer, docs
                ),
            }
        )
    passed = sum(case["passed"] for case in cases)
    return {
        "total": len(cases),
        "passed": passed,
        "pass_rate_pct": round(passed / len(cases) * 100, 2),
        "quality_avg": round(
            sum(case["quality_score"] for case in cases) / len(cases), 4
        ),
        "cases": cases,
    }


def main() -> None:
    report = evaluate()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({key: report[key] for key in report if key != "cases"}, indent=2))
    print(f"Wrote {OUTPUT}")
    raise SystemExit(0 if report["pass_rate_pct"] == 100 else 1)


if __name__ == "__main__":
    main()
