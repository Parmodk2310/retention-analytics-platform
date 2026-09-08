import numpy as np
import pytest

from app.ml.evaluate import (
    evaluate_binary,
    lift_at_k,
    recall_at_k,
)
from app.ml.threshold import choose_threshold


def test_evaluation_reports_prevalence_baseline() -> None:
    y_true = np.array([1, 1, 1, 1, 0])

    probabilities = np.array([0.90, 0.80, 0.70, 0.60, 0.20])

    metrics = evaluate_binary(
        y_true,
        probabilities,
        threshold=0.5,
    )

    assert metrics["prevalence"] == pytest.approx(0.8)

    assert metrics["pr_auc_baseline"] == pytest.approx(0.8)

    assert "balanced_accuracy" in metrics
    assert "mcc" in metrics
    assert "specificity" in metrics
    assert "recall_at_10pct" in metrics


def test_perfect_classifier_has_perfect_metrics() -> None:
    y_true = np.array([0, 0, 1, 1])

    probabilities = np.array([0.10, 0.20, 0.80, 0.90])

    metrics = evaluate_binary(
        y_true,
        probabilities,
        threshold=0.5,
    )

    assert metrics["roc_auc"] == pytest.approx(1.0)

    assert metrics["pr_auc"] == pytest.approx(1.0)

    assert metrics["balanced_accuracy"] == pytest.approx(1.0)

    assert metrics["f1"] == pytest.approx(1.0)

    assert metrics["mcc"] == pytest.approx(1.0)

    assert metrics["false_positive"] == 0
    assert metrics["false_negative"] == 0


def test_lift_and_recall_at_k() -> None:
    y_true = np.array([1, 1, 0, 0, 0, 0, 0, 0, 0, 0])

    probabilities = np.array(
        [
            0.99,
            0.90,
            0.80,
            0.70,
            0.60,
            0.50,
            0.40,
            0.30,
            0.20,
            0.10,
        ]
    )

    lift = lift_at_k(
        y_true,
        probabilities,
        k=0.2,
    )

    recall = recall_at_k(
        y_true,
        probabilities,
        k=0.2,
    )

    assert lift == pytest.approx(5.0)

    assert recall == pytest.approx(1.0)


def test_threshold_selection_uses_balanced_accuracy() -> None:
    y_true = np.array([1] * 80 + [0] * 20)

    probabilities = np.array([0.90] * 40 + [0.60] * 40 + [0.70] * 5 + [0.20] * 15)

    threshold, rows = choose_threshold(
        y_true,
        probabilities,
    )

    selected = min(
        rows,
        key=lambda row: abs(row["threshold"] - threshold),
    )

    best_balanced_accuracy = max(row["balanced_accuracy"] for row in rows)

    assert selected["balanced_accuracy"] == pytest.approx(best_balanced_accuracy)


def test_brier_skill_compares_against_prevalence_baseline() -> None:
    y = np.array([1, 1, 1, 0, 0])

    probabilities = np.array([0.9, 0.8, 0.7, 0.2, 0.1])

    metrics = evaluate_binary(
        y,
        probabilities,
    )

    assert metrics["brier_baseline"] > 0

    assert metrics["brier_skill_score"] > 0


def test_threshold_validation() -> None:
    y_true = np.array([0, 1])

    probabilities = np.array([0.2, 0.8])

    with pytest.raises(ValueError):
        choose_threshold(
            y_true,
            probabilities,
            minimum_threshold=0.9,
            maximum_threshold=0.1,
        )
