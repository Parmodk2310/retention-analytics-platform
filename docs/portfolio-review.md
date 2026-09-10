# Portfolio review guide

## Thirty-second summary

RetentionOS is an end-to-end product analytics case study: events enter through a reliable
asynchronous pipeline, PostgreSQL computes inspectable metrics, offline ML produces persisted churn
scores, and experimentation separates assignment from exposure before estimating effects.

## Five-minute review path

1. Read the root README capability and delivery-status tables.
2. Review `backend/app/analytics/queries/` for SQL-first metric definitions.
3. Review `backend/app/realtime/` and the worker for delivery semantics.
4. Review `backend/app/ml/` for temporal boundaries and artifact lineage.
5. Review `backend/app/experiments/` for assignment, SRM, power and decisions.
6. Review `frontend/src/pages/` for analyst workflows.
7. Review workflows, Terraform and OCI assets for delivery controls.

## Evidence map

| Claim | Evidence |
|---|---|
| Metrics are not hard-coded in the UI | SQL queries, typed routes and frontend API clients |
| Churn evaluation avoids temporal leakage | Snapshot boundaries, temporal tests and metadata |
| Exposure is modeled correctly | Separate assignment/exposure records and lifecycle validation |
| Event retries are safe | Stable IDs, recovery, ACK-after-commit and database uniqueness |
| Security is part of delivery | OIDC, immutable references, secret scanning and private data services |
| Operations are testable | Health endpoints, metrics, dashboards, alerts and runbooks |

## Current limitations

- Data is synthetic; observed patterns are demonstrations, not customer outcomes.
- AWS Terraform is validated but unapplied.
- OCI Compose passed local smoke tests but has no live VM while Singapore A1 capacity is unavailable.
- The OCI demo is single-node and intentionally not highly available.
- Legacy `/ml/churn/*` handlers are not the production scoring interface.

## Interview prompts

- Why does assignment differ from exposure?
- Why is PR-AUC more useful than accuracy for churn ranking?
- Where does at-least-once delivery create duplicate risk?
- When should SQL analytics move to aggregates or a warehouse?
- What changes for multi-AZ recovery, regulated data or ten times the traffic?

Strong answers connect each design choice to a failure mode and trade-off.
