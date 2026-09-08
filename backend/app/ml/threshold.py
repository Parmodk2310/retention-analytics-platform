import numpy as np
from sklearn.metrics import (
    balanced_accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)


def choose_threshold(
    y_true,
    probabilities,
    minimum_threshold: float = 0.05,
    maximum_threshold: float = 0.95,
    steps: int = 91,
) -> tuple[float, list[dict[str, float]]]:
    """
    Choose a decision threshold using validation data only.

    Balanced accuracy is the primary objective because churn
    prevalence is high and F1 alone can favor predicting nearly
    every user as churned.
    """

    if not 0 < minimum_threshold < 1:
        raise ValueError("minimum_threshold must be between 0 and 1.")

    if not 0 < maximum_threshold < 1:
        raise ValueError("maximum_threshold must be between 0 and 1.")

    if minimum_threshold >= maximum_threshold:
        raise ValueError("minimum_threshold must be less than maximum_threshold.")

    if steps < 2:
        raise ValueError("steps must be at least 2.")

    y = np.asarray(y_true)
    probabilities = np.asarray(probabilities)

    thresholds = np.linspace(
        minimum_threshold,
        maximum_threshold,
        steps,
    )

    rows: list[dict[str, float]] = []

    for threshold in thresholds:
        predictions = (probabilities >= threshold).astype(int)

        row = {
            "threshold": float(threshold),
            "balanced_accuracy": float(
                balanced_accuracy_score(
                    y,
                    predictions,
                )
            ),
            "precision": float(
                precision_score(
                    y,
                    predictions,
                    zero_division=0,
                )
            ),
            "recall": float(
                recall_score(
                    y,
                    predictions,
                    zero_division=0,
                )
            ),
            "f1": float(
                f1_score(
                    y,
                    predictions,
                    zero_division=0,
                )
            ),
        }

        rows.append(row)

    best = max(
        rows,
        key=lambda row: (
            row["balanced_accuracy"],
            row["f1"],
        ),
    )

    return best["threshold"], rows
