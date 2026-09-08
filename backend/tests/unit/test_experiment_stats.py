import pytest

from app.experiments.stats import analyze_binary


def test_positive_effect_is_detected():
    result = analyze_binary(
        control_conversions=950,
        control_n=10_000,
        treatment_conversions=1_050,
        treatment_n=10_000,
    )

    assert result["treatment_rate"] > result["control_rate"]
    assert result["absolute_lift"] > 0
    assert result["relative_lift"] > 0
    assert result["p_value"] < 0.05
    assert result["significant"] is True

    lower, upper = result["difference_ci"]
    assert lower > 0
    assert upper > lower


def test_no_effect_is_not_significant():
    result = analyze_binary(
        control_conversions=1_000,
        control_n=10_000,
        treatment_conversions=1_000,
        treatment_n=10_000,
    )

    assert result["absolute_lift"] == pytest.approx(0.0)
    assert result["p_value"] == pytest.approx(1.0)
    assert result["significant"] is False

    lower, upper = result["difference_ci"]
    assert lower < 0 < upper


def test_alpha_controls_confidence_interval():
    result_95 = analyze_binary(
        950,
        10_000,
        1_050,
        10_000,
        alpha=0.05,
    )

    result_99 = analyze_binary(
        950,
        10_000,
        1_050,
        10_000,
        alpha=0.01,
    )

    width_95 = result_95["difference_ci"][1] - result_95["difference_ci"][0]
    width_99 = result_99["difference_ci"][1] - result_99["difference_ci"][0]

    assert result_95["confidence_level"] == pytest.approx(0.95)
    assert result_99["confidence_level"] == pytest.approx(0.99)
    assert width_99 > width_95


def test_zero_control_rate_has_no_relative_lift():
    result = analyze_binary(
        control_conversions=0,
        control_n=1_000,
        treatment_conversions=10,
        treatment_n=1_000,
    )

    assert result["control_rate"] == 0
    assert result["relative_lift"] is None


@pytest.mark.parametrize(
    ("control_conversions", "control_n", "treatment_conversions", "treatment_n"),
    [
        (-1, 100, 10, 100),
        (101, 100, 10, 100),
        (10, 0, 10, 100),
        (10, 100, 101, 100),
        (10, 100, 10, 0),
    ],
)
def test_invalid_counts_are_rejected(
    control_conversions,
    control_n,
    treatment_conversions,
    treatment_n,
):
    with pytest.raises(ValueError):
        analyze_binary(
            control_conversions,
            control_n,
            treatment_conversions,
            treatment_n,
        )


@pytest.mark.parametrize("alpha", [0, 1, -0.01, 1.01])
def test_invalid_alpha_is_rejected(alpha):
    with pytest.raises(ValueError):
        analyze_binary(
            10,
            100,
            12,
            100,
            alpha=alpha,
        )
