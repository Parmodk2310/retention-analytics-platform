from datetime import UTC, datetime

RUNNING_STATUS = "running"

STATE_ACTIVE = "active"
STATE_SCHEDULED = "scheduled"
STATE_ENDED = "ended"

ERROR_NOT_RUNNING = "experiment_not_running"
ERROR_NOT_STARTED = "experiment_not_started"
ERROR_ENDED = "experiment_ended"


class ExperimentLifecycleError(ValueError):
    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def experiment_state(experiment, now: datetime | None = None) -> str:
    current = _as_utc(now or datetime.now(UTC))

    if experiment.status != RUNNING_STATUS:
        return str(experiment.status)

    if experiment.starts_at and current < _as_utc(experiment.starts_at):
        return STATE_SCHEDULED

    if experiment.ends_at and current >= _as_utc(experiment.ends_at):
        return STATE_ENDED

    return STATE_ACTIVE


def ensure_experiment_active(experiment, now: datetime | None = None) -> None:
    state = experiment_state(experiment, now)

    if state == STATE_ACTIVE:
        return

    if state == STATE_SCHEDULED:
        raise ExperimentLifecycleError(
            ERROR_NOT_STARTED,
            "experiment has not started",
        )

    if state == STATE_ENDED:
        raise ExperimentLifecycleError(
            ERROR_ENDED,
            "experiment has ended",
        )

    raise ExperimentLifecycleError(
        ERROR_NOT_RUNNING,
        f"experiment status '{experiment.status}' is not running",
    )
