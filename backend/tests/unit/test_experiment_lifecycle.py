from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest

from app.experiments.lifecycle import (
    ERROR_ENDED,
    ERROR_NOT_RUNNING,
    ERROR_NOT_STARTED,
    STATE_ACTIVE,
    STATE_ENDED,
    STATE_SCHEDULED,
    ExperimentLifecycleError,
    ensure_experiment_active,
    experiment_state,
)

NOW = datetime(2026, 9, 8, 12, 0, tzinfo=UTC)


def experiment(
    status="running",
    starts_at=None,
    ends_at=None,
):
    return SimpleNamespace(
        status=status,
        starts_at=starts_at,
        ends_at=ends_at,
    )


def test_running_experiment_is_active():
    exp = experiment()

    assert experiment_state(exp, NOW) == STATE_ACTIVE
    ensure_experiment_active(exp, NOW)


def test_start_boundary_is_inclusive():
    exp = experiment(starts_at=NOW)

    assert experiment_state(exp, NOW) == STATE_ACTIVE


def test_future_experiment_is_blocked():
    exp = experiment(starts_at=NOW + timedelta(hours=1))

    assert experiment_state(exp, NOW) == STATE_SCHEDULED

    with pytest.raises(ExperimentLifecycleError) as error:
        ensure_experiment_active(exp, NOW)

    assert error.value.code == ERROR_NOT_STARTED


def test_end_boundary_is_exclusive():
    exp = experiment(ends_at=NOW)

    assert experiment_state(exp, NOW) == STATE_ENDED

    with pytest.raises(ExperimentLifecycleError) as error:
        ensure_experiment_active(exp, NOW)

    assert error.value.code == ERROR_ENDED


@pytest.mark.parametrize("status", ["draft", "paused", "completed"])
def test_non_running_status_is_blocked(status):
    exp = experiment(status=status)

    with pytest.raises(ExperimentLifecycleError) as error:
        ensure_experiment_active(exp, NOW)

    assert error.value.code == ERROR_NOT_RUNNING


def test_active_window_is_allowed():
    exp = experiment(
        starts_at=NOW - timedelta(days=1),
        ends_at=NOW + timedelta(days=1),
    )

    assert experiment_state(exp, NOW) == STATE_ACTIVE
