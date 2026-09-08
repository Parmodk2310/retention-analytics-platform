import numpy as np

from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
)


def lift_at_k(
    y_true,
    probabilities,
    k: float = 0.1,
) -> float:
    """Return lift among the top-k fraction of scored users."""
    if not 0 < k <= 1:
        raise ValueError("k must be in (0, 1].")

    y = np.asarray(y_true)
    probabilities = np.asarray(probabilities)

    n = max(1, int(len(y) * k))

    top_indices = np.argsort(-probabilities)[:n]
    top_rate = y[top_indices].mean()

    base_rate = y.mean()

    if base_rate == 0:
        return 0.0

    return float(top_rate / base_rate)


def recall_at_k(
    y_true,
    probabilities,
    k: float = 0.1,
) -> float:
    """Return fraction of positives captured in top-k scores."""
    if not 0 < k <= 1:
        raise ValueError("k must be in (0, 1].")

    y = np.asarray(y_true)
    probabilities = np.asarray(probabilities)

    total_positives = y.sum()

    if total_positives == 0:
        return 0.0

    n = max(1, int(len(y) * k))

    top_indices = np.argsort(-probabilities)[:n]
    captured = y[top_indices].sum()

    return float(captured / total_positives)


def evaluate_binary(
    y_true,
    probabilities,
    threshold: float = 0.5,
) -> dict[str, float | int]:
    """Evaluate binary churn probabilities and decisions."""

    y = np.asarray(y_true)
    probabilities = np.asarray(probabilities)

    predictions = (probabilities >= threshold).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y,
        predictions,
        labels=[0, 1],
    ).ravel()

    # ---------------------------------------------------------
    # Basic dataset statistics
    # ---------------------------------------------------------

    prevalence = float(y.mean())

    # ---------------------------------------------------------
    # Ranking metrics
    # ---------------------------------------------------------

    pr_auc = float(
        average_precision_score(
            y,
            probabilities,
        )
    )

    if prevalence < 1.0:
        normalized_pr_auc = float((pr_auc - prevalence) / (1.0 - prevalence))
    else:
        normalized_pr_auc = 0.0

    # ROC-AUC requires both classes to be present.
    if len(np.unique(y)) == 2:
        roc_auc = float(
            roc_auc_score(
                y,
                probabilities,
            )
        )
    else:
        roc_auc = 0.0

    # ---------------------------------------------------------
    # Classification metrics
    # ---------------------------------------------------------

    specificity = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0

    precision = float(
        precision_score(
            y,
            predictions,
            zero_division=0,
        )
    )

    recall = float(
        recall_score(
            y,
            predictions,
            zero_division=0,
        )
    )

    balanced_accuracy = float(
        balanced_accuracy_score(
            y,
            predictions,
        )
    )

    f1 = float(
        f1_score(
            y,
            predictions,
            zero_division=0,
        )
    )

    mcc = float(
        matthews_corrcoef(
            y,
            predictions,
        )
    )

    # ---------------------------------------------------------
    # Brier score
    # ---------------------------------------------------------

    # Model Brier score.
    model_brier = float(
        brier_score_loss(
            y,
            probabilities,
        )
    )

    # Baseline model:
    # predict the observed churn prevalence for every user.
    baseline_probabilities = np.full(
        len(y),
        prevalence,
        dtype=float,
    )

    brier_baseline = float(
        brier_score_loss(
            y,
            baseline_probabilities,
        )
    )

    # Brier Skill Score:
    #
    # BSS = 1 - (model Brier / baseline Brier)
    #
    # Positive value  -> model beats baseline
    # Zero             -> model equals baseline
    # Negative value   -> model is worse than baseline
    brier_skill_score = float(1.0 - (model_brier / brier_baseline)) if brier_baseline > 0 else 0.0

    # ---------------------------------------------------------
    # Return metrics
    # ---------------------------------------------------------

    return {
        "prevalence": prevalence,
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
        "pr_auc_baseline": prevalence,
        "normalized_pr_auc": normalized_pr_auc,
        "precision": precision,
        "recall": recall,
        "specificity": specificity,
        "balanced_accuracy": balanced_accuracy,
        "f1": f1,
        "mcc": mcc,
        "brier": model_brier,
        "brier_baseline": brier_baseline,
        "brier_skill_score": brier_skill_score,
        "lift_at_10pct": lift_at_k(
            y,
            probabilities,
            0.1,
        ),
        "recall_at_10pct": recall_at_k(
            y,
            probabilities,
            0.1,
        ),
        "threshold": float(threshold),
        "true_negative": int(tn),
        "false_positive": int(fp),
        "false_negative": int(fn),
        "true_positive": int(tp),
    }
