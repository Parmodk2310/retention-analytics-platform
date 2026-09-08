import pytest

from app.experiments.effect_size import binary_effect_size


def test_positive_effect():
    result = binary_effect_size(0.10, 0.11)

    assert result["risk_difference"] == pytest.approx(0.01)
    assert result["relative_lift"] == pytest.approx(0.10)
    assert result["risk_ratio"] == pytest.approx(1.10)
    assert result["odds_ratio"] > 1
    assert result["number_needed"] == pytest.approx(100)
    assert result["number_needed_type"] == "nnt"
    assert result["direction"] == "positive"


def test_negative_effect():
    result = binary_effect_size(0.10, 0.09)

    assert result["risk_difference"] == pytest.approx(-0.01)
    assert result["risk_ratio"] < 1
    assert result["odds_ratio"] < 1
    assert result["number_needed"] == pytest.approx(100)
    assert result["number_needed_type"] == "nnh"
    assert result["direction"] == "negative"


def test_neutral_effect():
    result = binary_effect_size(0.10, 0.10)

    assert result["risk_difference"] == 0
    assert result["risk_ratio"] == pytest.approx(1.0)
    assert result["number_needed"] is None
    assert result["number_needed_type"] is None
    assert result["direction"] == "neutral"


def test_zero_control_rate_has_no_relative_metrics():
    result = binary_effect_size(0.0, 0.01)

    assert result["relative_lift"] is None
    assert result["risk_ratio"] is None
    assert result["odds_ratio"] is None


@pytest.mark.parametrize(
    ("control_rate", "treatment_rate"),
    [
        (-0.1, 0.1),
        (1.1, 0.1),
        (0.1, -0.1),
        (0.1, 1.1),
        (float("nan"), 0.1),
    ],
)
def test_invalid_rates_are_rejected(control_rate, treatment_rate):
    with pytest.raises(ValueError):
        binary_effect_size(control_rate, treatment_rate)
