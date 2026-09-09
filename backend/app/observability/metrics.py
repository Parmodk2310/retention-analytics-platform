from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
)

HTTP_REQUESTS = Counter("http_requests_total", "HTTP requests", ["method", "path", "status"])
HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds", "HTTP request duration", ["method", "path"]
)
ANALYTICS_QUERY_DURATION = Histogram(
    "analytics_query_duration_seconds", "Analytics query duration", ["query"]
)
EXPERIMENT_EXPOSURES = Counter(
    "experiment_exposures_total", "Experiment exposures", ["experiment", "variant"]
)
CHURN_PREDICTIONS = Counter("churn_predictions_total", "Persisted churn predictions", ["risk_band"])

EVENT_PIPELINE_QUEUED = Counter(
    "retention_event_pipeline_queued_total",
    "Events accepted into the Redis ingestion stream",
)

EVENT_PIPELINE_BACKPRESSURE = Counter(
    "retention_event_pipeline_backpressure_total",
    "Event batches rejected by pipeline backpressure",
)

EVENT_PIPELINE_PERSISTED = Counter(
    "retention_event_pipeline_persisted_total",
    "Events successfully persisted to PostgreSQL",
)

EVENT_PIPELINE_DUPLICATES = Counter(
    "retention_event_pipeline_duplicates_total",
    "Duplicate events rejected during persistence",
)

EVENT_PIPELINE_DEAD_LETTER = Counter(
    "retention_event_pipeline_dead_letter_total",
    "Messages moved to the event dead-letter stream",
)

EVENT_PIPELINE_RECOVERED = Counter(
    "retention_event_pipeline_recovered_total",
    "Pending messages reclaimed for retry",
)

EVENT_WORKER_FAILURES = Counter(
    "retention_event_worker_failures_total",
    "Unhandled event-worker iteration failures",
)

EVENT_PIPELINE_BACKLOG = Gauge(
    "retention_event_pipeline_backlog",
    "Current event stream pending plus undelivered lag",
)

EVENT_PIPELINE_PENDING = Gauge(
    "retention_event_pipeline_pending",
    "Current pending messages in the consumer group",
)

EVENT_PIPELINE_LAG = Gauge(
    "retention_event_pipeline_lag",
    "Current undelivered consumer-group messages",
)

EVENT_PIPELINE_FRESHNESS_SECONDS = Gauge(
    "retention_event_pipeline_freshness_seconds",
    "Seconds since successful event persistence",
)

EVENT_PIPELINE_LAST_PERSISTED = Gauge(
    "retention_event_pipeline_last_persisted_unixtime",
    "Unix timestamp of latest event persistence",
)

EVENT_PIPELINE_BATCH_SIZE = Histogram(
    "retention_event_pipeline_batch_size",
    "Number of events processed in a persistence batch",
    buckets=(
        1,
        10,
        25,
        50,
        100,
        250,
        500,
    ),
)

EVENT_PIPELINE_PERSIST_DURATION = Histogram(
    "retention_event_pipeline_persist_seconds",
    "Event persistence duration",
    buckets=(
        0.005,
        0.01,
        0.025,
        0.05,
        0.1,
        0.25,
        0.5,
        1,
        2,
    ),
)
