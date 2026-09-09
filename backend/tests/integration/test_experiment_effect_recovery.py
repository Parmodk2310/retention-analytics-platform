import os

import pytest
from sqlalchemy import select

from app.db.models import Experiment
from app.db.session import AsyncSessionLocal
from app.schemas.experiment import ExperimentResults
from app.services.experiment_service import results

pytestmark = pytest.mark.skipif(
    not os.getenv("TEST_DATABASE_URL"),
    reason="set TEST_DATABASE_URL to run integration tests",
)


EXPERIMENT_KEY = "onboarding_v2"
EXPECTED_METRIC = "purchase_rate_14d"

MIN_MATURE_USERS_PER_VARIANT = 20_000
MIN_RECOVERED_RELATIVE_LIFT = 0.03
MAX_RECOVERED_RELATIVE_LIFT = 0.20


@pytest.mark.asyncio
async def test_synthetic_treatment_effect_is_recovered():
    async with AsyncSessionLocal() as db:
        experiment = await db.scalar(select(Experiment).where(Experiment.key == EXPERIMENT_KEY))

        assert experiment is not None

        output = ExperimentResults.model_validate(await results(db, experiment))

    variants = {variant.variant: variant for variant in output.variants}

    assert output.metric.key == EXPECTED_METRIC
    assert {"control", "treatment"} <= variants.keys()

    control = variants["control"]
    treatment = variants["treatment"]

    assert control.n >= MIN_MATURE_USERS_PER_VARIANT
    assert treatment.n >= MIN_MATURE_USERS_PER_VARIANT

    assert output.srm.tested is True
    assert output.srm.detected is False

    analysis = output.analysis
    assert analysis is not None

    assert treatment.conversion_rate > control.conversion_rate
    assert analysis.absolute_lift > 0
    assert analysis.relative_lift is not None
    assert MIN_RECOVERED_RELATIVE_LIFT <= analysis.relative_lift <= MAX_RECOVERED_RELATIVE_LIFT

    assert analysis.significant is True
    assert analysis.p_value < analysis.alpha
    assert analysis.difference_ci[0] > 0

    assert analysis.effect_size.direction == "positive"
    assert analysis.effect_size.risk_ratio is not None
    assert analysis.effect_size.risk_ratio > 1

    assert output.decision == "ship_treatment"
