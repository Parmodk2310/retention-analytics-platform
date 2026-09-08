from datetime import UTC, datetime, timedelta
from typing import cast
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Experiment, ExperimentAssignment
from app.experiments.lifecycle import ExperimentLifecycleError
from app.services.experiment_service import expose, get_or_assign

NOW = datetime.now(UTC)


def make_experiment(
    status: str = "running",
    starts_at: datetime | None = None,
    ends_at: datetime | None = None,
) -> Experiment:
    return Experiment(
        id=uuid4(),
        key=f"test_{uuid4().hex[:8]}",
        name="Lifecycle test",
        hypothesis="Treatment improves conversion.",
        primary_metric="purchase_rate_14d",
        variants=["control", "treatment"],
        traffic_allocation={"control": 0.5, "treatment": 0.5},
        status=status,
        starts_at=starts_at,
        ends_at=ends_at,
    )


def make_db(scalar_result=None) -> tuple[AsyncSession, AsyncMock]:
    mock = AsyncMock(spec=AsyncSession)
    mock.scalar.return_value = scalar_result
    return cast(AsyncSession, mock), mock


@pytest.mark.asyncio
async def test_existing_assignment_survives_completed_experiment():
    exp = make_experiment(status="completed")
    user_id = uuid4()
    assignment = ExperimentAssignment(
        experiment_id=exp.id,
        user_id=user_id,
        variant="control",
    )
    db, _ = make_db(assignment)

    result = await get_or_assign(db, exp, user_id)

    assert result is assignment


@pytest.mark.asyncio
async def test_new_assignment_is_blocked_when_experiment_completed():
    exp = make_experiment(status="completed")
    db, _ = make_db()

    with pytest.raises(ExperimentLifecycleError):
        await get_or_assign(db, exp, uuid4())


@pytest.mark.asyncio
async def test_new_assignment_is_blocked_before_start():
    exp = make_experiment(starts_at=NOW + timedelta(days=1))
    db, _ = make_db()

    with pytest.raises(ExperimentLifecycleError):
        await get_or_assign(db, exp, uuid4())


@pytest.mark.asyncio
async def test_exposure_is_blocked_after_end():
    exp = make_experiment(ends_at=NOW - timedelta(seconds=1))
    db, _ = make_db()

    with pytest.raises(ExperimentLifecycleError):
        await expose(db, exp, uuid4())
