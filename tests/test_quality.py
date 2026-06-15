from scripts.benchmark_cost import benchmark
from scripts.evaluate_quality import evaluate


def test_expected_answers_all_pass() -> None:
    report = evaluate()

    assert report["pass_rate_pct"] == 100
    assert report["quality_avg"] >= 0.9


def test_cost_optimization_reduces_tokens_and_cost() -> None:
    report = benchmark()

    assert report["token_reduction_pct"] >= 50
    assert report["cost_reduction_pct"] >= 40
