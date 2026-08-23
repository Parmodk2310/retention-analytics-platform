import math
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
import numpy as np
from scipy import stats
from statsmodels.stats.proportion import proportions_ztest, proportion_confint
from statsmodels.stats.power import NormalIndPower


@dataclass
class ABTestResult:
    control_rate: float
    treatment_rate: float
    relative_lift: float
    absolute_diff: float
    p_value: float
    significant: bool
    ci_control: Tuple[float, float]
    ci_treatment: Tuple[float, float]
    sample_size_control: int
    sample_size_treatment: int
    power: float
    recommendation: str


class ABTestAnalyzer:
    """
    Statistical engine for A/B testing.
    Supports proportion metrics (conversion rates) and continuous metrics (revenue).
    """
    
    def __init__(self, alpha: float = 0.05):
        self.alpha = alpha
    
    def analyze_proportions(
        self,
        control_conversions: int,
        control_size: int,
        treatment_conversions: int,
        treatment_size: int,
        mde: Optional[float] = None
    ) -> ABTestResult:
        """
        Z-test for proportion metrics.
        
        Example: Onboarding activation rate
        Control: 324/1000 = 32.4%
        Treatment: 365/1000 = 36.5%
        Result: p=0.004, significant at α=0.05
        """
        if control_size == 0 or treatment_size == 0:
            raise ValueError("Sample sizes must be greater than 0")
        
        count = np.array([treatment_conversions, control_conversions])
        nobs = np.array([treatment_size, control_size])
        
        # Two-sided Z-test
        z_stat, p_value = proportions_ztest(count, nobs, alternative='two-sided')
        
        # Wilson confidence intervals (more accurate for small samples)
        ci_low_treat, ci_high_treat = proportion_confint(
            treatment_conversions, treatment_size, alpha=self.alpha, method='wilson'
        )
        ci_low_ctrl, ci_high_ctrl = proportion_confint(
            control_conversions, control_size, alpha=self.alpha, method='wilson'
        )
        
        p_treat = treatment_conversions / treatment_size
        p_ctrl = control_conversions / control_size
        relative_lift = (p_treat - p_ctrl) / p_ctrl if p_ctrl > 0 else 0
        absolute_diff = p_treat - p_ctrl
        
        # Calculate observed power
        power = self._calculate_power(p_ctrl, p_treat, control_size, treatment_size)
        
        # Recommendation logic
        if p_value < self.alpha and relative_lift > 0:
            recommendation = "🟢 Launch treatment — statistically significant positive lift"
        elif p_value < self.alpha and relative_lift < 0:
            recommendation = "🔴 Do not launch — statistically significant negative impact"
        else:
            recommendation = "🟡 Inconclusive — consider running longer or increasing sample size"
        
        return ABTestResult(
            control_rate=round(p_ctrl, 4),
            treatment_rate=round(p_treat, 4),
            relative_lift=round(relative_lift, 4),
            absolute_diff=round(absolute_diff, 4),
            p_value=round(p_value, 5),
            significant=p_value < self.alpha,
            ci_control=(round(ci_low_ctrl, 4), round(ci_high_ctrl, 4)),
            ci_treatment=(round(ci_low_treat, 4), round(ci_high_treat, 4)),
            sample_size_control=control_size,
            sample_size_treatment=treatment_size,
            power=round(power, 2),
            recommendation=recommendation
        )
    
    def analyze_continuous(
        self,
        control_values: np.ndarray,
        treatment_values: np.ndarray
    ) -> Dict:
        """
        Welch's t-test for continuous metrics (revenue, session duration).
        Does not assume equal variances.
        """
        t_stat, p_value = stats.ttest_ind(treatment_values, control_values, equal_var=False)
        
        mean_ctrl = np.mean(control_values)
        mean_treat = np.mean(treatment_values)
        lift = (mean_treat - mean_ctrl) / mean_ctrl if mean_ctrl != 0 else 0
        
        # Confidence interval for difference in means
        se = np.sqrt(
            np.var(treatment_values, ddof=1) / len(treatment_values) +
            np.var(control_values, ddof=1) / len(control_values)
        )
        df = self._welch_df(control_values, treatment_values)
        t_crit = stats.t.ppf(1 - self.alpha/2, df)
        diff = mean_treat - mean_ctrl
        
        return {
            "control_mean": round(mean_ctrl, 2),
            "treatment_mean": round(mean_treat, 2),
            "relative_lift": round(lift, 4),
            "p_value": round(p_value, 5),
            "significant": p_value < self.alpha,
            "ci_diff": (round(diff - t_crit * se, 2), round(diff + t_crit * se, 2)),
            "degrees_of_freedom": round(df, 1)
        }
    
    def required_sample_size(
        self,
        baseline_rate: float,
        mde: float,
        alpha: float = 0.05,
        power: float = 0.8,
        ratio: float = 1.0
    ) -> int:
        """
        Pre-experiment power analysis.
        Returns required sample size PER VARIANT.
        """
        effect_size = abs(mde) / math.sqrt(baseline_rate * (1 - baseline_rate))
        analysis = NormalIndPower()
        n = analysis.solve_power(
            effect_size=effect_size,
            alpha=alpha,
            power=power,
            ratio=ratio
        )
        return math.ceil(n)
    
    def _calculate_power(
        self,
        p1: float,
        p2: float,
        n1: int,
        n2: int,
        alpha: float = 0.05
    ) -> float:
        """Post-hoc power calculation."""
        pooled_se = math.sqrt(
            p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2
        )
        z_alpha = stats.norm.ppf(1 - alpha / 2)
        z_beta = (abs(p2 - p1) - z_alpha * pooled_se) / pooled_se
        return stats.norm.cdf(z_beta)
    
    def _welch_df(self, a: np.ndarray, b: np.ndarray) -> float:
        """Welch-Satterthwaite degrees of freedom."""
        var_a = np.var(a, ddof=1)
        var_b = np.var(b, ddof=1)
        n_a, n_b = len(a), len(b)
        
        numerator = (var_a / n_a + var_b / n_b) ** 2
        denominator = (var_a / n_a) ** 2 / (n_a - 1) + (var_b / n_b) ** 2 / (n_b - 1)
        return numerator / denominator if denominator > 0 else 1