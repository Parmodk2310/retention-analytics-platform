# System Design

The platform is an event-based product analytics application. The React SPA calls FastAPI through `/api/v1`. PostgreSQL is the source of truth for users, events, experiments, exposures, model runs, and persisted churn scores. Redis supports token revocation, rate limiting/cache and durable event ingestion through Redis Streams. Analytics are SQL-first. ML training is offline; web requests never retrain the model.

## Production request path

`CloudFront -> S3 SPA` for static assets and `CloudFront /api/* -> ALB -> ECS Fargate -> RDS/ElastiCache` for API calls. Keeping the API behind the same CloudFront distribution avoids mixed-content issues and simplifies CORS.

## Reliability boundaries

- `/health/live` is process liveness.
- `/health/ready` validates PostgreSQL and Redis.
- All event writes are idempotent by `event_id`.
- Analytics requests are bounded by explicit date ranges.
- Model scores are persisted in `churn_scores`, so dashboard latency is independent of XGBoost inference cost.
