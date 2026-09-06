from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize


def required_sample_size(
    baseline: float, mde_absolute: float, alpha: float = 0.05, power: float = 0.8
) -> int:
    effect = abs(proportion_effectsize(baseline, baseline + mde_absolute))
    return int(
        NormalIndPower().solve_power(
            effect_size=effect, power=power, alpha=alpha, ratio=1, alternative="two-sided"
        )
        + 0.999
    )
