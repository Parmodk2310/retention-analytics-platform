from dataclasses import dataclass
from typing import Any

import numpy as np
from sklearn.linear_model import LogisticRegression


EPSILON = 1e-6


def probability_logit(
    probabilities,
) -> np.ndarray:
    probabilities = np.asarray(
        probabilities,
        dtype=float,
    )

    probabilities = np.clip(
        probabilities,
        EPSILON,
        1.0 - EPSILON,
    )

    return np.log(probabilities / (1.0 - probabilities)).reshape(-1, 1)


@dataclass
class SigmoidCalibratedModel:
    """
    Wrap a fitted classifier with Platt-style
    sigmoid probability calibration.
    """

    base_model: Any
    calibrator: LogisticRegression

    def predict_proba(
        self,
        frame,
    ) -> np.ndarray:
        raw_probability = self.base_model.predict_proba(frame)[:, 1]

        calibrated_probability = self.calibrator.predict_proba(probability_logit(raw_probability))[
            :, 1
        ]

        return np.column_stack(
            [
                1.0 - calibrated_probability,
                calibrated_probability,
            ]
        )

    @property
    def classes_(self) -> np.ndarray:
        return np.array([0, 1])


def fit_sigmoid_calibrator(
    base_model,
    X_calibration,
    y_calibration,
) -> SigmoidCalibratedModel:
    raw_probability = base_model.predict_proba(X_calibration)[:, 1]

    calibrator = LogisticRegression(
        max_iter=1000,
        random_state=42,
    )

    calibrator.fit(
        probability_logit(raw_probability),
        np.asarray(y_calibration),
    )

    if calibrator.coef_[0][0] <= 0:
        raise RuntimeError("Calibration slope must be positive.")

    return SigmoidCalibratedModel(
        base_model=base_model,
        calibrator=calibrator,
    )
