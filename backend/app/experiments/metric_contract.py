from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BinaryMetric:
    key: str
    event_name: str
    window_days: int
    label: str


METRICS = {
    "purchase_rate_7d": BinaryMetric(
        key="purchase_rate_7d",
        event_name="purchase",
        window_days=7,
        label="7-day purchase conversion",
    ),
    "purchase_rate_14d": BinaryMetric(
        key="purchase_rate_14d",
        event_name="purchase",
        window_days=14,
        label="14-day purchase conversion",
    ),
    "purchase_rate_30d": BinaryMetric(
        key="purchase_rate_30d",
        event_name="purchase",
        window_days=30,
        label="30-day purchase conversion",
    ),
}

METRIC_ALIASES = {
    "activation_rate": "purchase_rate_14d",
}


def resolve_metric(metric_key: str) -> BinaryMetric:
    key = metric_key.strip().lower()
    key = METRIC_ALIASES.get(key, key)

    try:
        return METRICS[key]
    except KeyError as exc:
        raise ValueError(f"unsupported experiment metric: {metric_key}") from exc
