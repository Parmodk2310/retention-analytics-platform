import pytest

from app.experiments.power import power_diagnostics


def test_large_sample_detects_target_effect():
    result = power_diagnostics(
        control_rate=0.10,
        control_n=60_000,
        treatment_n=60_000,
        target_relative_lift=0.05,
    )

    assert result["power_at_target_effect"] > 0.8
    assert result["adequately_powered_for_target"] is True
    assert result["mde_absolute"] > 0
    assert result["mde_relative"] > 0


def test_small_sample_has_lower_power():
    small = power_diagnostics(
        control_rate=0.10,
        control_n=1_000,
        treatment_n=1_000,
        target_relative_lift=0.05,
    )

    large = power_diagnostics(
        control_rate=0.10,
        control_n=25_000,
        treatment_n=25_000,
        target_relative_lift=0.05,
    )

    assert small["power_at_target_effect"] < large["power_at_target_effect"]
    assert small["mde_absolute"] > large["mde_absolute"]


def test_required_sample_size_is_positive():
    result = power_diagnostics(
        control_rate=0.10,
        control_n=5_000,
        treatment_n=5_000,
    )

    assert result["required_control_n"] > 0
    assert result["required_treatment_n"] > 0


def test_unequal_allocation_is_supported():
    result = power_diagnostics(
        control_rate=0.10,
        control_n=10_000,
        treatment_n=20_000,
    )

    assert result["allocation_ratio"] == pytest.approx(2.0)


@pytest.mark.parametrize(
    ("control_rate", "control_n", "treatment_n"),
    [
        (0.0, 100, 100),
        (1.0, 100, 100),
        (-0.1, 100, 100),
        (0.1, 0, 100),
        (0.1, 100, 0),
        (0.1, -1, 100),
    ],
)
def test_invalid_inputs_are_rejected(
    control_rate,
    control_n,
    treatment_n,
):
    with pytest.raises(ValueError):
        power_diagnostics(
            control_rate,
            control_n,
            treatment_n,
        )


@pytest.mark.parametrize(
    "target_relative_lift",
    [0, -0.1, float("nan")],
)
def test_invalid_target_lift_is_rejected(target_relative_lift):
    with pytest.raises(ValueError):
        power_diagnostics(
            0.10,
            1_000,
            1_000,
            target_relative_lift=target_relative_lift,
        )
