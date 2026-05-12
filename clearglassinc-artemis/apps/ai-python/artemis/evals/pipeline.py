"""Offline eval + auto-proposal + drift/rollback logic for the self-improvement loop."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class EvalReport:
    candidate_version: str
    precision: float
    recall: float
    latency_p95_ms: float
    false_positive_rate: float
    operator_trust_score: float = 5.0
    precision_delta: float = 0.0
    latency_delta: float = 0.0


def evaluate_candidate(
    candidate_version: str,
    eval_set: list[dict[str, Any]],
    run_candidate: Callable[[str, Any], tuple[int, float]],
) -> EvalReport:
    tp = fp = fn = 0
    latencies: list[float] = []
    for sample in eval_set:
        pred, latency_ms = run_candidate(candidate_version, sample["input"])
        latencies.append(latency_ms)
        label = sample["label"]
        if pred == 1 and label == 1:
            tp += 1
        elif pred == 1 and label == 0:
            fp += 1
        elif pred == 0 and label == 1:
            fn += 1
    eps = 1e-9
    precision = tp / (tp + fp + eps)
    recall = tp / (tp + fn + eps)
    latencies.sort()
    p95 = latencies[min(len(latencies) - 1, int(0.95 * len(latencies)))] if latencies else 0.0
    fpr = fp / (fp + (len(eval_set) - tp - fp - fn) + eps)
    return EvalReport(candidate_version, precision, recall, p95, fpr)


def propose_upgrade(report: EvalReport) -> dict[str, Any] | None:
    """Only low-risk, clearly-positive candidates get proposed — and always require human approval."""
    if report.precision_delta > 0.03 and report.latency_delta < 0.05:
        return {
            "type": "prompt_update",
            "to_version": report.candidate_version,
            "risk": "low",
            "requires_human_approval": True,
        }
    return None


def should_rollback(metrics: dict[str, float]) -> bool:
    return any(
        [
            metrics.get("precision", 1.0) < 0.82,
            metrics.get("latency_p95_ms", 0.0) > 1800,
            metrics.get("operator_trust_score", 5.0) < 4.0,
            metrics.get("false_positive_rate", 0.0) > 0.18,
        ]
    )
