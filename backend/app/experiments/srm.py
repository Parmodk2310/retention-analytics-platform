import math
from numbers import Integral

from scipy.stats import binomtest, chisquare

from app.experiments.assignment import validate_assignment_contract

DEFAULT_SRM_ALPHA = 0.01
MIN_EXPECTED_COUNT = 5.0


def _validate_srm_inputs(
    observed: dict[str, int],
    allocation: dict[str, float],
    alpha: float,
) -> tuple[list[str], dict[str, int]]:
    variants = sorted(allocation)
    validate_assignment_contract(variants, allocation)

    if not math.isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError("SRM alpha must be between 0 and 1")

    unknown = set(observed) - set(allocation)
    if unknown:
        raise ValueError("observed variants must match experiment allocation")

    normalized = {}

    for variant in variants:
        value = observed.get(variant, 0)

        if isinstance(value, bool) or not isinstance(value, Integral) or value < 0:
            raise ValueError("observed counts must be non-negative integers")

        normalized[variant] = int(value)

    return variants, normalized


def _pearson_statistic(
    observed: list[int],
    expected: list[float],
) -> float:
    return sum(((obs - exp) ** 2) / exp for obs, exp in zip(observed, expected, strict=True))


def sample_ratio_mismatch(
    observed: dict[str, int],
    allocation: dict[str, float],
    alpha: float = DEFAULT_SRM_ALPHA,
) -> dict:
    variants, observed = _validate_srm_inputs(observed, allocation, alpha)

    total = sum(observed.values())
    expected = {variant: total * allocation[variant] for variant in variants}

    base = {
        "alpha": alpha,
        "total": total,
        "observed": observed,
        "expected": {key: round(value, 2) for key, value in expected.items()},
    }

    if total == 0:
        return {
            **base,
            "method": "not_tested",
            "tested": False,
            "detected": False,
            "chi_square": 0.0,
            "p_value": 1.0,
            "reason": "no_exposures",
        }

    obs = [observed[v] for v in variants]
    exp = [expected[v] for v in variants]
    chi_square = _pearson_statistic(obs, exp)

    if len(variants) == 2:
        first = variants[0]

        result = binomtest(
            observed[first],
            total,
            allocation[first],
            alternative="two-sided",
        )

        return {
            **base,
            "method": "exact_binomial",
            "tested": True,
            "detected": bool(result.pvalue < alpha),
            "chi_square": float(chi_square),
            "p_value": float(result.pvalue),
            "reason": None,
        }

    if min(exp) < MIN_EXPECTED_COUNT:
        return {
            **base,
            "method": "not_tested",
            "tested": False,
            "detected": False,
            "chi_square": float(chi_square),
            "p_value": 1.0,
            "reason": "insufficient_expected_count",
        }

    statistic, p_value = chisquare(obs, f_exp=exp)

    return {
        **base,
        "method": "pearson_chi_square",
        "tested": True,
        "detected": bool(p_value < alpha),
        "chi_square": float(statistic),
        "p_value": float(p_value),
        "reason": None,
    }
