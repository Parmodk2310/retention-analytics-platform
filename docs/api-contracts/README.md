# API contracts

The FastAPI application exposes versioned routes below `/api/v1`. Interactive OpenAPI
documentation is available at `/docs` in local development and is the canonical field-level
schema. This document records ownership, authentication and behavior that schema generation alone
does not explain.

## Authentication model

- Access tokens are sent as `Authorization: Bearer <token>`.
- Refresh tokens use an HttpOnly cookie scoped to `/api/v1/auth`.
- Register and login are limited to five attempts per minute.
- Analytics, churn, experiment and system routes require an authenticated account.
- Event ingestion uses `X-Event-Ingest-Key` outside local development.

## Endpoint inventory

| Method | Path | Protection | Purpose |
|---|---|---|---|
| GET | `/health/live` | Public | Process liveness only |
| GET | `/health/ready` | Public | PostgreSQL and Redis readiness |
| POST | `/auth/register` | Public, rate-limited | Create account and issue tokens |
| POST | `/auth/login` | Public, rate-limited | Authenticate and issue tokens |
| POST | `/auth/refresh` | Refresh cookie | Rotate the refresh token |
| POST | `/auth/logout` | Refresh cookie | Revoke refresh token and clear cookie |
| GET | `/auth/me` | Bearer token | Return current account |
| POST | `/events/batch` | Ingest key, rate-limited | Queue a validated event batch; returns 202 |
| GET | `/analytics/overview` | Bearer token | Headline activity and revenue metrics |
| GET | `/analytics/activity` | Bearer token | Time-series activity |
| GET | `/analytics/funnel` | Bearer token | Ordered product funnel |
| GET | `/analytics/retention` | Bearer token | Cohort retention cells |
| GET | `/analytics/revenue` | Bearer token | Revenue time series |
| GET | `/analytics/channels` | Bearer token | Acquisition-channel comparison |
| GET | `/churn/scores` | Bearer token | Paginated persisted scores |
| GET | `/churn/scores/{user_id}` | Bearer token | Latest score for one user |
| GET | `/churn/summary` | Bearer token | Latest scoring summary |
| GET | `/churn/model-health` | Bearer token | Model lineage, metrics and health metadata |
| POST | `/experiments` | Bearer token | Create an experiment |
| GET | `/experiments` | Bearer token | List experiments |
| POST | `/experiments/{id}/assign/{user_id}` | Bearer token | Idempotent deterministic assignment |
| POST | `/experiments/{id}/expose/{user_id}` | Bearer token | Record actual treatment exposure |
| GET | `/experiments/{id}/results` | Bearer token | SRM and treatment-effect analysis |
| GET | `/system/event-pipeline` | Bearer token | Backlog, lag and freshness status |
| GET | `/system/info` | Bearer token | Version, environment and feature flags |

All paths above are prefixed by `/api/v1`.

## Query bounds

- Analytics day ranges are limited to 1–365 days; activity requires at least seven days.
- Retention and revenue accept 1–24 months.
- Churn score pages accept 1–100 rows with a non-negative offset.
- Churn risk bands are `low`, `medium`, `high` or `critical`.

## Important compatibility note

`POST /ml/churn/predict` and `GET /ml/churn/user/{user_id}` exist in source as compatibility
contracts but are not included by the current API router and return HTTP 501 if mounted. Production
dashboard data comes from the persisted-score `/churn/*` endpoints. Do not document synchronous
model inference as an active capability.

## Failure semantics

- `401`: missing, invalid or revoked authentication.
- `404`: requested experiment, user, score or model run does not exist.
- `409`: invalid experiment lifecycle transition or duplicate account.
- `422`: request or query validation failure.
- `503`: event backlog exceeded the admission limit; clients should honor `Retry-After`.

Event transport is at least once. Clients must supply stable event identifiers and tolerate
idempotent duplicate handling.
