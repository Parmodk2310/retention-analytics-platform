import math
from numbers import Integral

import numpy as np
from scipy.stats import norm
from statsmodels.stats.proportion import proportions_ztest

DEFAULT_ALPHA = 0.05


def _validate_binary_counts(
    control_conversions: int,
    control_n: int,
    treatment_conversions: int,
    treatment_n: int,
    alpha: float,
) -> None:
    values = {
        "control_conversions": control_conversions,
        "control_n": control_n,
        "treatment_conversions": treatment_conversions,
        "treatment_n": treatment_n,
    }

    for name, value in values.items():
        if isinstance(value, bool) or not isinstance(value, Integral):
            raise ValueError(f"{name} must be an integer")

        if value < 0:
            raise ValueError(f"{name} must be non-negative")

    if control_n == 0 or treatment_n == 0:
        raise ValueError("both variants require observations")

    if control_conversions > control_n:
        raise ValueError("control conversions cannot exceed observations")

    if treatment_conversions > treatment_n:
        raise ValueError("treatment conversions cannot exceed observations")

    if not math.isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError("alpha must be between 0 and 1")


def analyze_binary(
    control_conversions: int,
    control_n: int,
    treatment_conversions: int,
    treatment_n: int,
    alpha: float = DEFAULT_ALPHA,
) -> dict:
    _validate_binary_counts(
        control_conversions,
        control_n,
        treatment_conversions,
        treatment_n,
        alpha,
    )

    control_rate = control_conversions / control_n
    treatment_rate = treatment_conversions / treatment_n
    difference = treatment_rate - control_rate

    counts = np.array(
        [treatment_conversions, control_conversions],
        dtype=float,
    )
    observations = np.array(
        [treatment_n, control_n],
        dtype=float,
    )

    z_stat, p_value = proportions_ztest(
        counts,
        observations,
        alternative="two-sided",
    )

    standard_error = math.sqrt(
        treatment_rate * (1 - treatment_rate) / treatment_n
        + control_rate * (1 - control_rate) / control_n
    )

    confidence_level = 1 - alpha
    critical_value = float(norm.ppf(1 - alpha / 2))
    lower = difference - critical_value * standard_error
    upper = difference + critical_value * standard_error

    significant = bool(p_value < alpha)

    return {
        "control_rate": control_rate,
        "treatment_rate": treatment_rate,
        "absolute_lift": difference,
        "relative_lift": difference / control_rate if control_rate else None,
        "standard_error": standard_error,
        "z_stat": float(z_stat),
        "p_value": float(p_value),
        "difference_ci": [lower, upper],
        "confidence_level": confidence_level,
        "alpha": alpha,
        "significant": significant,
    }
