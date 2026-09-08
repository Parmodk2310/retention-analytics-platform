import numpy as np

from app.ml.threshold import choose_threshold


def test_choose_threshold_returns_valid_threshold() -> None:
    y_true = np.array([0, 0, 1, 1])
    probabilities = np.array([0.1, 0.3, 0.7, 0.9])

    threshold, rows = choose_threshold(
        y_true,
        probabilities,
    )

    assert 0.05 <= threshold <= 0.95
    assert rows
    assert all("f1" in row for row in rows)


def test_choose_threshold_is_deterministic() -> None:
    y_true = np.array([0, 1, 0, 1])
    probabilities = np.array([0.2, 0.8, 0.4, 0.9])

    first, _ = choose_threshold(
        y_true,
        probabilities,
    )

    second, _ = choose_threshold(
        y_true,
        probabilities,
    )

    assert first == second