import pytest

from app.experiments.srm import sample_ratio_mismatch


def test_balanced_two_variant_experiment_has_no_srm():
    result = sample_ratio_mismatch(
        {"control": 500, "treatment": 500},
        {"control": 0.5, "treatment": 0.5},
    )

    assert result["tested"] is True
    assert result["detected"] is False
    assert result["method"] == "exact_binomial"
    assert result["p_value"] > 0.01


def test_large_two_variant_mismatch_is_detected():
    result = sample_ratio_mismatch(
        {"control": 900, "treatment": 100},
        {"control": 0.5, "treatment": 0.5},
    )

    assert result["tested"] is True
    assert result["detected"] is True
    assert result["p_value"] < 0.01


def test_zero_exposures_are_not_tested():
    result = sample_ratio_mismatch(
        {"control": 0, "treatment": 0},
        {"control": 0.5, "treatment": 0.5},
    )

    assert result["tested"] is False
    assert result["detected"] is False
    assert result["reason"] == "no_exposures"


def test_multi_variant_experiment_uses_chi_square():
    result = sample_ratio_mismatch(
        {
            "control": 300,
            "treatment_a": 300,
            "treatment_b": 400,
        },
        {
            "control": 0.3,
            "treatment_a": 0.3,
            "treatment_b": 0.4,
        },
    )

    assert result["tested"] is True
    assert result["method"] == "pearson_chi_square"
    assert result["detected"] is False


def test_small_multi_variant_sample_is_not_tested():
    result = sample_ratio_mismatch(
        {
            "control": 2,
            "treatment_a": 2,
            "treatment_b": 2,
        },
        {
            "control": 0.34,
            "treatment_a": 0.33,
            "treatment_b": 0.33,
        },
    )

    assert result["tested"] is False
    assert result["reason"] == "insufficient_expected_count"


@pytest.mark.parametrize(
    "observed",
    [
        {"control": -1, "treatment": 10},
        {"control": 1.5, "treatment": 10},
        {"control": True, "treatment": 10},
    ],
)
def test_invalid_observed_counts_are_rejected(observed):
    with pytest.raises(ValueError):
        sample_ratio_mismatch(
            observed,
            {"control": 0.5, "treatment": 0.5},
        )


@pytest.mark.parametrize("alpha", [0, 1, -0.1, 1.1])
def test_invalid_alpha_is_rejected(alpha):
    with pytest.raises(ValueError):
        sample_ratio_mismatch(
            {"control": 50, "treatment": 50},
            {"control": 0.5, "treatment": 0.5},
            alpha=alpha,
        )
