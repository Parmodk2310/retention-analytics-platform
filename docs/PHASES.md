# Phase 0 → Phase 8 implementation map

This file maps the requested build phases to the source files included in the repository.

## Phase 0 — Foundation / repository boot

Primary files:

- `.env.example`
- `.dockerignore`
- `.gitignore`
- `.pre-commit-config.yaml`
- `docker-compose.yml`
- `Makefile`
- `backend/Dockerfile`
- `backend/requirements.txt`
- `backend/requirements-dev.txt`
- `backend/pyproject.toml`
- `backend/alembic.ini`
- `backend/app/main.py`
- `backend/app/core/config.py`
- `backend/app/core/logging.py`
- `backend/app/core/middleware.py`
- `backend/app/core/exceptions.py`
- `backend/app/core/rate_limit.py`
- `backend/app/db/base.py`
- `backend/app/db/session.py`
- `backend/app/api/router.py`
- `backend/app/api/deps.py`
- `backend/app/api/v1/health.py`
- `frontend/package.json`
- `frontend/tsconfig.json`
- `frontend/vite.config.ts`
- `frontend/index.html`
- `frontend/nginx.conf`
- `frontend/Dockerfile`
- `frontend/src/main.tsx`
- `frontend/src/App.tsx`
- `frontend/src/index.css`

Exit criteria: PostgreSQL and Redis healthy, Alembic applies, FastAPI readiness returns 200,
frontend builds and renders.

## Phase 1 — Synthetic event data / schema

Primary files:

- `backend/alembic/versions/001_initial_schema.py`
- `backend/alembic/versions/002_experiment_exposures.py`
- `backend/alembic/versions/003_churn_scores.py`
- `backend/alembic/versions/004_analytics_indexes.py`
- `backend/app/db/models/*`
- `backend/app/schemas/event.py`
- `backend/app/db/repositories/event_repository.py`
- `backend/app/services/event_service.py`
- `backend/app/api/v1/events.py`
- `data-generator/config.py`
- `data-generator/seed.py`
- `data-generator/validate.py`
- `data-generator/generators/users.py`
- `data-generator/generators/lifecycle.py`
- `data-generator/generators/sessions.py`
- `data-generator/generators/funnel.py`
- `data-generator/generators/experiments.py`
- `data-generator/generators/revenue.py`

Exit criteria: 12-month event history, signup events, positive purchases, stable 50/50 experiment
assignment, realistic channel differences, and validation passes.

## Phase 2 — SQL product analytics

Primary files:

- `backend/app/analytics/executor.py`
- `backend/app/analytics/queries/overview.sql`
- `backend/app/analytics/queries/activity.sql`
- `backend/app/analytics/queries/funnel.sql`
- `backend/app/analytics/queries/retention.sql`
- `backend/app/analytics/queries/revenue.sql`
- `backend/app/analytics/queries/channel_performance.sql`
- `backend/app/db/repositories/analytics_repository.py`
- `backend/app/services/analytics_service.py`
- `backend/app/services/funnel_service.py`
- `backend/app/services/cohort_service.py`
- `backend/app/api/v1/analytics.py`
- `backend/tests/unit/test_funnel.py`
- `backend/tests/unit/test_retention.py`

Exit criteria: real DAU/WAU/MAU/stickiness, ordered funnel, UTC cohort retention and revenue/channel
metrics available through API endpoints.

## Phase 3 — Product frontend

Primary files:

- `frontend/src/app/*`
- `frontend/src/components/ui/*`
- `frontend/src/components/layout/*`
- `frontend/src/components/charts/*`
- `frontend/src/components/filters/*`
- `frontend/src/hooks/useAnalytics.ts`
- `frontend/src/lib/*`
- `frontend/src/pages/Dashboard.tsx`
- `frontend/src/pages/ProductMetrics.tsx`
- `frontend/src/pages/FunnelAnalysis.tsx`
- `frontend/src/pages/CohortAnalysis.tsx`
- `frontend/src/services/analyticsApi.ts`
- `frontend/src/types/*`

Exit criteria: no hard-coded business KPIs; loading/error/empty states are present and metrics come
from the backend.

## Phase 4 — Churn ML

Primary files:

- `backend/app/ml/dataset.py`
- `backend/app/ml/features.py`
- `backend/app/ml/labels.py`
- `backend/app/ml/pipeline.py`
- `backend/app/ml/train.py`
- `backend/app/ml/evaluate.py`
- `backend/app/ml/predict.py`
- `backend/app/ml/explain.py`
- `backend/app/ml/artifact_store.py`
- `backend/app/jobs/score_churn.py`
- `backend/app/jobs/monitor_model.py`
- `backend/app/db/models/model_run.py`
- `backend/app/db/models/churn_score.py`
- `backend/app/services/churn_service.py`
- `backend/app/api/v1/churn.py`
- `frontend/src/pages/ChurnPrediction.tsx`
- `frontend/src/pages/ModelHealth.tsx`
- `frontend/src/services/mlApi.ts`
- `frontend/src/components/churn/*`
- `backend/tests/unit/test_churn_features.py`

Exit criteria: future-window labels, temporal split, baseline vs XGBoost comparison, persisted model,
persisted scores and model health UI.

## Phase 5 — Experimentation

Primary files:

- `backend/app/experiments/assignment.py`
- `backend/app/experiments/eligibility.py`
- `backend/app/experiments/metrics.py`
- `backend/app/experiments/srm.py`
- `backend/app/experiments/power.py`
- `backend/app/experiments/cuped.py`
- `backend/app/experiments/stats.py`
- `backend/app/experiments/decision.py`
- `backend/app/services/experiment_service.py`
- `backend/app/api/v1/experiments.py`
- `backend/app/schemas/experiment.py`
- `frontend/src/pages/Experiments.tsx`
- `frontend/src/pages/ExperimentDetail.tsx`
- `frontend/src/components/experiments/*`
- `frontend/src/services/experimentApi.ts`
- `backend/tests/unit/test_randomization.py`
- `backend/tests/unit/test_srm.py`
- `backend/tests/unit/test_statistics.py`

Exit criteria: assignment, exposure, SRM, inference and experiment decisions are internally
consistent and reproducible.

## Phase 6 — Authentication / application security

Primary files:

- `backend/app/core/security.py`
- `backend/app/api/deps.py`
- `backend/app/api/v1/auth.py`
- `backend/app/schemas/auth.py`
- `backend/app/db/models/user.py`
- `frontend/src/pages/Login.tsx`
- `frontend/src/services/authApi.ts`
- `frontend/src/services/api.ts`
- `frontend/src/store/authStore.ts`
- `SECURITY.md`
- `docs/security/threat-model.md`
- `.github/workflows/security.yml`

Exit criteria: Argon2 credentials, short-lived JWTs, HttpOnly refresh tokens, token rotation,
protected APIs, event-ingestion key, rate limiting, request validation and secret scanning.

## Phase 7 — Realtime / observability / polish ✅

Primary files:

- `backend/app/observability/metrics.py`
- `backend/app/observability/tracing.py`
- `backend/app/realtime/event_stream.py`
- `backend/app/realtime/event_consumer.py`
- `backend/app/realtime/event_freshness.py`
- `backend/app/jobs/consume_events.py`
- `backend/app/jobs/refresh_aggregates.py`
- `backend/app/api/v1/system.py`
- `backend/app/schemas/system.py`
- `frontend/src/pages/Settings.tsx`
- `frontend/src/services/systemApi.ts`
- `monitoring/prometheus/*`
- `monitoring/grafana/*`
- `monitoring/alertmanager/*`
- `infrastructure/docker-compose.monitoring.yml`

Exit criteria: durable Redis Streams ingestion, consumer-group recovery, idempotent PostgreSQL
persistence, metrics endpoint, dashboards/alerts, error-tracing hooks and pipeline freshness.

Phase 7 freeze validation:

- backend: 167 passed, 4 skipped
- frontend: 8 tests passed
- Gitleaks: passed
- pip-audit: no known vulnerabilities
- npm audit: 0 vulnerabilities
- Prometheus targets: API and event worker healthy
- Prometheus alert rules: 7/7 healthy
- Grafana health: database OK
- Alertmanager readiness: HTTP 200
- event pipeline: backlog 0, pending 0 and consumer lag 0 during runtime verification

Product polish completed in this phase:

- typed system-health and event-pipeline contracts
- recruiter-facing System Health UI
- daily revenue visualization for ranges up to 90 days and monthly visualization for longer ranges
- human-readable global and local churn/TreeSHAP feature labels

## Phase 8 — AWS / IaC / CI-CD

Primary files:

- `infrastructure/terraform/main.tf`
- `infrastructure/terraform/variables.tf`
- `infrastructure/terraform/outputs.tf`
- `infrastructure/terraform/versions.tf`
- `infrastructure/terraform/modules/networking/*`
- `infrastructure/terraform/modules/alb/*`
- `infrastructure/terraform/modules/ecr/*`
- `infrastructure/terraform/modules/ecs/*`
- `infrastructure/terraform/modules/rds/*`
- `infrastructure/terraform/modules/redis/*`
- `infrastructure/terraform/modules/static_site/*`
- `infrastructure/terraform/modules/monitoring/*`
- `infrastructure/terraform/modules/scheduled_jobs/*`
- `infrastructure/terraform/environments/staging/*`
- `infrastructure/terraform/environments/production/*`
- `.github/workflows/ci-backend.yml`
- `.github/workflows/ci-frontend.yml`
- `.github/workflows/deploy-staging.yml`
- `.github/workflows/deploy-production.yml`
- `.github/workflows/deploy-aws.yml`
- `.github/dependabot.yml`
- `.github/CODEOWNERS`
- `scripts/bootstrap.sh`
- `scripts/seed-dev.sh`
- `scripts/smoke-test.sh`
- `scripts/benchmark.sh`

Exit criteria: reproducible AWS infrastructure, image build/push, migration/seed/train/score bootstrapping,
frontend S3/CloudFront deployment and CI/security checks.
