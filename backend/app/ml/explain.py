from typing import Any

import numpy as np
import pandas as pd
import xgboost as xgb

from app.ml.features import FEATURES


def base_pipeline(model: Any):
    """
    Return the underlying sklearn pipeline.

    Calibrated models wrap the original fitted pipeline
    in `base_model`.
    """
    return getattr(
        model,
        "base_model",
        model,
    )


def model_components(model: Any):
    pipeline = base_pipeline(model)

    if not hasattr(
        pipeline,
        "named_steps",
    ):
        raise TypeError("Model does not contain a sklearn pipeline.")

    preprocess = pipeline.named_steps["preprocess"]

    estimator = pipeline.named_steps["model"]

    return preprocess, estimator


def clean_feature_name(
    name: str,
) -> str:
    return name.replace(
        "num__",
        "",
    ).replace(
        "cat__",
        "",
    )


def transformed_feature_names(
    model: Any,
) -> list[str]:
    preprocess, _ = model_components(model)

    return [clean_feature_name(str(name)) for name in (preprocess.get_feature_names_out())]


def global_feature_importance(
    model: Any,
    top_n: int = 20,
) -> list[dict[str, float | str]]:
    """
    Return global model importance.

    XGBoost uses feature_importances_.
    Linear models fall back to absolute coefficients.
    """

    preprocess, estimator = model_components(model)

    names = [clean_feature_name(str(name)) for name in (preprocess.get_feature_names_out())]

    values = getattr(
        estimator,
        "feature_importances_",
        None,
    )

    if values is None:
        coefficients = getattr(
            estimator,
            "coef_",
            None,
        )

        if coefficients is None:
            return []

        values = np.abs(np.asarray(coefficients).reshape(-1))

    values = np.asarray(
        values,
        dtype=float,
    )

    order = np.argsort(-values)[:top_n]

    return [
        {
            "feature": names[index],
            "importance": float(values[index]),
        }
        for index in order
    ]


def shap_reason_codes(
    model: Any,
    frame: pd.DataFrame,
    top_n: int = 3,
) -> list[list[dict[str, float | str]]]:
    """
    Generate local TreeSHAP reason codes using
    XGBoost's native pred_contribs implementation.

    The final column returned by XGBoost is the
    bias/base-value contribution and is excluded
    from user-facing reason codes.
    """

    if frame.empty:
        return []

    if top_n < 1:
        raise ValueError("top_n must be at least 1.")

    preprocess, estimator = model_components(model)

    transformed = preprocess.transform(frame[FEATURES])

    names = [clean_feature_name(str(name)) for name in (preprocess.get_feature_names_out())]

    if not hasattr(
        estimator,
        "get_booster",
    ):
        raise TypeError("Local SHAP reason codes currently require an XGBoost estimator.")

    booster = estimator.get_booster()

    matrix = xgb.DMatrix(transformed)

    contributions = booster.predict(
        matrix,
        pred_contribs=True,
    )

    contributions = np.asarray(
        contributions,
        dtype=float,
    )

    if contributions.ndim != 2:
        raise RuntimeError("Unexpected XGBoost contribution shape.")

    expected_columns = len(names) + 1

    if contributions.shape[1] != expected_columns:
        raise RuntimeError("XGBoost contribution count does not match transformed feature count.")

    # Last column is the model bias/base value.
    feature_contributions = contributions[:, :-1]

    results: list[list[dict[str, float | str]]] = []

    for row_values in feature_contributions:
        positive_indices = np.where(row_values > 0)[0]

        if len(positive_indices) > 0:
            order = positive_indices[np.argsort(-row_values[positive_indices])]
        else:
            order = np.argsort(-np.abs(row_values))

        reasons: list[dict[str, float | str]] = []

        for index in order[:top_n]:
            impact = float(row_values[index])

            reasons.append(
                {
                    "feature": (names[index]),
                    "impact": impact,
                    "direction": ("increases_risk" if impact > 0 else "reduces_risk"),
                }
            )

        results.append(reasons)

    return results
