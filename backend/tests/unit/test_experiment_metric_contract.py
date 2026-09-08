import pytest

from app.experiments.metric_contract import resolve_metric


@pytest.mark.parametrize(
    ("metric_key", "event", "days"),
    [
        ("purchase_rate_7d", "purchase", 7),
        ("purchase_rate_14d", "purchase", 14),
        ("purchase_rate_30d", "purchase", 30),
    ],
)
def test_metric_registry(metric_key, event, days):
    metric = resolve_metric(metric_key)

    assert metric.event_name == event
    assert metric.window_days == days


def test_activation_rate_alias_is_supported():
    metric = resolve_metric("activation_rate")

    assert metric.key == "purchase_rate_14d"


def test_metric_lookup_is_normalized():
    metric = resolve_metric(" PURCHASE_RATE_14D ")

    assert metric.key == "purchase_rate_14d"


def test_unknown_metric_is_rejected():
    with pytest.raises(ValueError, match="unsupported experiment metric"):
        resolve_metric("unknown_metric")
