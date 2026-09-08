import numpy as np
import pandas as pd

from app.ml.calibration import (
    fit_sigmoid_calibrator,
)


class DummyModel:
    def predict_proba(
        self,
        frame,
    ):
        probability = np.asarray(
            frame["probability"],
            dtype=float,
        )

        return np.column_stack(
            [
                1.0 - probability,
                probability,
            ]
        )


def test_calibrated_probabilities_are_valid() -> None:
    frame = pd.DataFrame(
        {
            "probability": [
                0.1,
                0.2,
                0.4,
                0.7,
                0.9,
            ]
        }
    )

    y = np.array([0, 0, 0, 1, 1])

    model = fit_sigmoid_calibrator(
        DummyModel(),
        frame,
        y,
    )

    probabilities = model.predict_proba(frame)

    assert probabilities.shape == (
        5,
        2,
    )

    assert np.all(probabilities >= 0)

    assert np.all(probabilities <= 1)

    assert np.allclose(
        probabilities.sum(axis=1),
        1.0,
    )


def test_calibration_preserves_ranking() -> None:
    frame = pd.DataFrame(
        {
            "probability": [
                0.1,
                0.3,
                0.5,
                0.7,
                0.9,
            ]
        }
    )

    y = np.array([0, 0, 0, 1, 1])

    model = fit_sigmoid_calibrator(
        DummyModel(),
        frame,
        y,
    )

    scores = model.predict_proba(frame)[:, 1]

    assert np.all(np.diff(scores) > 0)
