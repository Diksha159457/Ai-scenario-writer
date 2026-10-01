"""Reliability eval: run every sample input through the generator and report.

    python -m src.evaluate                                  # default model
    python -m src.evaluate --models llama-3.3-70b-versatile llama-3.1-8b-instant
    python -m src.evaluate --repeats 3 --out outputs/eval_report.md

Metrics per model:
  first_try  — share of runs valid on the first attempt (prompt quality)
  final      — share of runs valid within the retry budget (system reliability)
  avg_tries  — mean attempts per run (cost multiplier)
  p50 / p95  — end-to-end latency including retries
  failures   — which check caused rejected attempts (json / schema / quality / provider)
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

try:
    from .generator import MODEL_NAME, Completion, GenerationReport, generate_with_report, groq_completion
except ImportError:  # pragma: no cover
    from generator import MODEL_NAME, Completion, GenerationReport, generate_with_report, groq_completion

ROOT = Path(__file__).resolve().parent.parent
SAMPLES = ROOT / "tests" / "test_inputs.json"


@dataclass
class ModelSummary:
    model: str
    runs: int
    first_try: float
    final: float
    avg_tries: float
    p50_s: float
    p95_s: float
    failures: Counter
    warnings: int


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, round(pct / 100 * (len(ordered) - 1)))
    return ordered[idx]


def summarise(model: str, reports: list[GenerationReport]) -> ModelSummary:
    latencies = [r.total_latency_s for r in reports]
    failures: Counter = Counter(a.error_kind for r in reports for a in r.attempts if not a.ok)
    n = len(reports) or 1
    return ModelSummary(
        model=model,
        runs=len(reports),
        first_try=sum(bool(r.attempts and r.attempts[0].ok) for r in reports) / n,
        final=sum(r.ok and not r.warnings for r in reports) / n,
        avg_tries=statistics.fmean(len(r.attempts) for r in reports) if reports else 0.0,
        p50_s=_percentile(latencies, 50),
        p95_s=_percentile(latencies, 95),
        failures=failures,
        warnings=sum(bool(r.warnings) for r in reports),
    )


def run_eval(
    samples: list[dict], models: list[str], repeats: int = 1, completion: Completion | None = None
) -> list[ModelSummary]:
    completion = completion or groq_completion()
    summaries = []
    for model in models:
        reports = [
            generate_with_report(sample, completion=completion, model=model)
            for sample in samples
            for _ in range(repeats)
        ]
        summaries.append(summarise(model, reports))
    return summaries


def to_markdown(summaries: list[ModelSummary]) -> str:
    lines = [
        "| Model | Runs | Valid 1st try | Valid after retries | Avg tries | p50 | p95 | Rejections by check |",
        "|---|:--:|:--:|:--:|:--:|:--:|:--:|---|",
    ]
    for s in summaries:
        fails = ", ".join(f"{k}: {v}" for k, v in s.failures.most_common()) or "—"
        lines.append(
            f"| `{s.model}` | {s.runs} | {s.first_try:.0%} | {s.final:.0%} | {s.avg_tries:.2f} "
            f"| {s.p50_s:.1f}s | {s.p95_s:.1f}s | {fails} |"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Scenario writer reliability eval")
    parser.add_argument("--models", nargs="+", default=[MODEL_NAME])
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--samples", type=Path, default=SAMPLES)
    parser.add_argument("--out", type=Path, help="Write the markdown table to this file")
    args = parser.parse_args(argv)

    samples = json.loads(args.samples.read_text(encoding="utf-8"))
    table = to_markdown(run_eval(samples, args.models, args.repeats))
    print(table)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(table + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
