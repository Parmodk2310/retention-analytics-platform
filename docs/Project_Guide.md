# Repository guide

This guide explains ownership and change flow. It avoids a brittle file-by-file catalog.

## Component map

| Path | Owns | Typical change |
|---|---|---|
| `backend/app/api/` | HTTP contracts and dependencies | Route, protection or validation |
| `backend/app/analytics/` | SQL execution and metric definitions | Product metric |
| `backend/app/db/` | Sessions, models and repositories | Schema or persistence |
| `backend/app/experiments/` | Assignment, SRM, statistics and decisions | Experiment method |
| `backend/app/ml/` | Features, training, evaluation and artifacts | Model lifecycle |
| `backend/app/realtime/` | Redis Streams behavior | Delivery reliability |
| `backend/app/jobs/` | Worker, scoring and scheduled tasks | Offline operation |
| `frontend/src/` | Typed analyst interface and API clients | User workflow |
| `data-generator/` | Reproducible synthetic behavior | Demo data |
| `monitoring/` | Prometheus, Grafana and Alertmanager | Operational signal |
| `infrastructure/terraform/` | AWS reference architecture | Cloud infrastructure |
| `infrastructure/oci/` | Cost-aware demo operations | Single-node deployment |
| `.github/workflows/` | CI, security and deployment gates | Delivery policy |

## Change by concern

### API or database

Update the route/schema, preserve protection, add tests and update the API contract. Database
changes require a forward migration, repository updates and data-model documentation.

### Analytics

Define the metric and time boundary first. Modify parameterized SQL, add edge-case tests, verify
query bounds and update the API/UI. Do not implement business KPIs in React.

### ML

Protect feature/label time boundaries, use temporal validation, compare with the baseline, persist
preprocessing with the estimator and version metadata.

### Experimentation

Keep eligibility, assignment, exposure and outcome windows distinct. Verify SRM before interpreting
treatment effects.

### Event pipeline

Preserve stable IDs, ACK-after-commit, pending recovery, bounded batches and DLQ behavior. Test
duplicates and partial failures.

### Deployment

Keep cloud deployment gated. Pin third-party references, validate Compose/Terraform, document cost
impact and never commit secrets or generated plans.

## Local workflow

```bash
cp .env.example .env
docker compose up -d postgres redis
docker compose run --rm backend alembic upgrade head
docker compose up -d backend event-worker frontend
```

Use the root README for tests, data generation and ML jobs.

## Definition of done

- relevant automated tests and lint/build checks pass;
- contracts and runbooks remain accurate;
- migrations and retries are safe;
- no secrets or customer data enter Git;
- state is described honestly as implemented, validated or live;
- the pull request explains risk, evidence and rollback.
