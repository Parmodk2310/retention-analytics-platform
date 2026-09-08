from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.schemas.experiment import ExperimentCreate


def payload():
    return {
        "key": "checkout_copy_v1",
        "name": "Checkout copy test",
        "hypothesis": "Treatment improves purchase conversion.",
        "primary_metric": "purchase_conversion",
        "variants": ["control", "treatment"],
        "traffic_allocation": {
            "control": 0.5,
            "treatment": 0.5,
        },
    }


def test_valid_experiment():
    experiment = ExperimentCreate(**payload())

    assert experiment.variants == ["control", "treatment"]
    assert sum(experiment.traffic_allocation.values()) == pytest.approx(1.0)


@pytest.mark.parametrize(
    ("variants", "allocation"),
    [
        (["control", "control"], {"control": 1.0}),
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
def test_invalid_experiment_contract(variants, allocation):
    data = payload()
    data["variants"] = variants
    data["traffic_allocation"] = allocation

    with pytest.raises(ValidationError):
        ExperimentCreate(**data)


def test_invalid_experiment_window():
    data = payload()
    data["starts_at"] = datetime(2026, 9, 10, tzinfo=UTC)
    data["ends_at"] = datetime(2026, 9, 9, tzinfo=UTC)

    with pytest.raises(ValidationError):
        ExperimentCreate(**data)
