import pytest

from app.experiments.assignment import (
    BUCKET_COUNT,
    assign_variant,
    bucket_for,
    validate_assignment_contract,
)


def test_bucket_is_stable_and_bounded():
    first = bucket_for("user-1", "experiment-1")
    second = bucket_for("user-1", "experiment-1")

    assert first == second
    assert 0 <= first < BUCKET_COUNT


def test_assignment_is_deterministic():
    allocation = {"control": 0.5, "treatment": 0.5}
    variants = ["control", "treatment"]

    first = assign_variant(
        "user-1",
        "experiment-1",
        allocation,
        variants=variants,
    )
    second = assign_variant(
        "user-1",
        "experiment-1",
        allocation,
        variants=variants,
    )

    assert first == second


def test_assignment_uses_explicit_variant_order():
    variants = ["control", "treatment"]

    first = assign_variant(
        "user-1",
        "experiment-1",
        {"control": 0.5, "treatment": 0.5},
        variants=variants,
    )
    second = assign_variant(
        "user-1",
        "experiment-1",
        {"treatment": 0.5, "control": 0.5},
        variants=variants,
    )

    assert first == second


@pytest.mark.parametrize(
    ("variants", "allocation"),
    [
        (["control", "control"], {"control": 1.0}),
        (["control", "treatment"], {"control": 0.5}),
        (
            ["control", "treatment"],
            {"control": 1.0, "treatment": 0.0},
        ),
        (
            ["control", "treatment"],
            {"control": 0.4, "treatment": 0.4},
        ),
    ],
)
def test_invalid_assignment_contract_is_rejected(variants, allocation):
    with pytest.raises(ValueError):
        validate_assignment_contract(variants, allocation)
