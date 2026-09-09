from unittest.mock import Mock

from app.observability import metrics


def test_event_pipeline_metrics_are_registered():
    assert metrics.EVENT_PIPELINE_QUEUED._name == "retention_event_pipeline_queued"
    assert metrics.EVENT_PIPELINE_BACKLOG._name == "retention_event_pipeline_backlog"
    assert metrics.EVENT_PIPELINE_PERSISTED._name == "retention_event_pipeline_persisted"


def test_pipeline_counter_accepts_increment(monkeypatch):
    increment = Mock()

    monkeypatch.setattr(
        metrics.EVENT_PIPELINE_QUEUED,
        "inc",
        increment,
    )

    metrics.EVENT_PIPELINE_QUEUED.inc(10)

    increment.assert_called_once_with(10)
