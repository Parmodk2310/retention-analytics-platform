import math

DEFAULT_EPSILON = 1e-12


def _validate_rate(rate: float, name: str) -> None:
    if not math.isfinite(rate) or not 0 <= rate <= 1:
        raise ValueError(f"{name} must be between 0 and 1")


def binary_effect_size(
    control_rate: float,
    treatment_rate: float,
) -> dict:
    _validate_rate(control_rate, "control_rate")
    _validate_rate(treatment_rate, "treatment_rate")

    difference = treatment_rate - control_rate
    relative_lift = difference / control_rate if control_rate > 0 else None
    risk_ratio = treatment_rate / control_rate if control_rate > 0 else None

    control_odds = control_rate / (1 - control_rate) if 0 < control_rate < 1 else None
    treatment_odds = treatment_rate / (1 - treatment_rate) if 0 < treatment_rate < 1 else None

    odds_ratio = (
        treatment_odds / control_odds if control_odds and treatment_odds is not None else None
    )

    number_needed = 1 / abs(difference) if abs(difference) > DEFAULT_EPSILON else None

    direction = (
        "positive"
        if difference > DEFAULT_EPSILON
        else "negative"
        if difference < -DEFAULT_EPSILON
        else "neutral"
    )

    return {
        "risk_difference": difference,
        "relative_lift": relative_lift,
        "risk_ratio": risk_ratio,
        "odds_ratio": odds_ratio,
        "number_needed": number_needed,
        "number_needed_type": (
            "nnt" if direction == "positive" else "nnh" if direction == "negative" else None
        ),
        "direction": direction,
    }
