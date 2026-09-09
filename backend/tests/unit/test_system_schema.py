from datetime import UTC, datetime

from app.schemas.system import EventPipelineStatus, SystemFeatures, SystemInfo


def test_system_info_contract() -> None:
    info = SystemInfo(
        environment="test",
        version="1.0.0",
        features=SystemFeatures(
            realtime=True,
            churn_ml=True,
            experimentation=True,
        ),
    )

    assert info.environment == "test"
    assert info.version == "1.0.0"
    assert info.features.realtime is True


def test_event_pipeline_status_contract() -> None:
    now = datetime.now(UTC)

    status = EventPipelineStatus(
        status="fresh",
        last_persisted_at=now,
        latest_event_time=now,
        last_stream_id="1-0",
        freshness_seconds=1.5,
        pending=2,
        lag=3,
        backlog=5,
    )

    assert status.backlog == 5
    assert status.pending + status.lag == status.backlog
