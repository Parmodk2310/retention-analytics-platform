# Event Pipeline

## Architecture

Client → FastAPI → Redis Streams → consumer group → PostgreSQL.

## Delivery semantics

- At-least-once transport.
- Stable event identity before enqueue.
- Request and persistence deduplication.
- PostgreSQL uniqueness is the final concurrency-safe defense.
- Messages are ACKed only after successful persistence.
- Failed messages remain pending for recovery.
- Poison messages are isolated in a bounded DLQ.

## Reliability

- Pending-message recovery.
- Maximum delivery threshold before DLQ.
- Bounded PostgreSQL persistence batches.
- Admission backpressure with HTTP 503 and Retry-After.
- No destructive MAXLEN trimming on the primary ingestion stream.

## Freshness

Successful persistence updates a Redis freshness watermark.

Active analytics views refresh within approximately 30 seconds.

## Observability

Prometheus monitors:

- queued events
- persisted events
- duplicates
- retries
- DLQ activity
- backpressure
- stream backlog
- pending messages
- consumer lag
- freshness
- persistence latency

Grafana provides an event-pipeline dashboard and Alertmanager receives pipeline alerts.

## Local benchmark

Environment: local Docker Desktop / WSL2.

- Events: 2,000
- Persisted: 2,000
- Publish time: 0.113 s
- End-to-end time: 2.621 s
- Throughput: 763.06 events/s
- Final backlog: 0
- Pending: 0
- Consumer lag: 0
- Database restored to 1,176,283 synthetic events after cleanup.

This benchmark characterizes the local development environment and is not presented as a production-cloud throughput guarantee.