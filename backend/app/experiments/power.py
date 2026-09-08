import math
from typing import Any

from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

DEFAULT_ALPHA = 0.05
DEFAULT_TARGET_POWER = 0.80
DEFAULT_TARGET_RELATIVE_LIFT = 0.05


def _validate_probability(value: float, name: str) -> None:
    if not math.isfinite(value) or not 0 < value < 1:
        raise ValueError(f"{name} must be between 0 and 1")


def _validate_sample_size(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")


def _treatment_rate_from_effect(control_rate: float, effect_size: float) -> float:
    angle = math.asin(math.sqrt(control_rate)) + effect_size / 2
    return min(1.0, max(0.0, math.sin(angle) ** 2))


def power_diagnostics(
    control_rate: float,
    control_n: int,
    treatment_n: int,
    *,
    alpha: float = DEFAULT_ALPHA,
    target_power: float = DEFAULT_TARGET_POWER,
    target_relative_lift: float = DEFAULT_TARGET_RELATIVE_LIFT,
) -> dict:
    _validate_probability(control_rate, "control_rate")
    _validate_probability(alpha, "alpha")
    _validate_probability(target_power, "target_power")
    _validate_sample_size(control_n, "control_n")
    _validate_sample_size(treatment_n, "treatment_n")

    if not math.isfinite(target_relative_lift) or target_relative_lift <= 0:
        raise ValueError("target_relative_lift must be positive")

    ratio = treatment_n / control_n
    solver_ratio: Any = ratio
    target_treatment_rate = control_rate * (1 + target_relative_lift)

    if target_treatment_rate >= 1:
        raise ValueError("target relative lift produces an invalid treatment rate")

    solver = NormalIndPower()
    target_effect = abs(proportion_effectsize(target_treatment_rate, control_rate))

    power_at_target = solver.power(
        effect_size=target_effect,
        nobs1=control_n,
        alpha=alpha,
        ratio=solver_ratio,
        alternative="two-sided",
    )

    required_effect = solver.solve_power(
        effect_size=None,
        nobs1=control_n,
        alpha=alpha,
        power=target_power,
        ratio=solver_ratio,
        alternative="two-sided",
    )

    mde_treatment_rate = _treatment_rate_from_effect(
        control_rate,
        abs(float(required_effect)),
    )
    mde_absolute = mde_treatment_rate - control_rate

    required_control_n = math.ceil(
        float(
            solver.solve_power(
                effect_size=target_effect,
                nobs1=None,
                alpha=alpha,
                power=target_power,
                ratio=solver_ratio,
                alternative="two-sided",
            )
        )
    )
    required_treatment_n = math.ceil(required_control_n * ratio)

    return {
        "alpha": alpha,
        "target_power": target_power,
        "allocation_ratio": ratio,
        "control_n": control_n,
        "treatment_n": treatment_n,
        "target_relative_lift": target_relative_lift,
        "target_absolute_lift": target_treatment_rate - control_rate,
        "power_at_target_effect": float(power_at_target),
        "mde_absolute": mde_absolute,
        "mde_relative": mde_absolute / control_rate,
        "required_control_n": required_control_n,
        "required_treatment_n": required_treatment_n,
        "adequately_powered_for_target": bool(power_at_target >= target_power),
    }
