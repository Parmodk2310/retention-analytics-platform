# User Retention & Experimentation Analytics Platform

Production-style product analytics project for retention, funnel analysis, cohort retention,
churn prediction, and A/B experimentation. The repository is organized as a monorepo and is
intended to demonstrate the engineering depth expected from a Product Data Scientist / ML
Engineer with roughly 2–3 years of practical experience.

## Core capabilities

- 50,000-user / 1.2M+ event synthetic product dataset
- DAU / WAU / MAU / stickiness / revenue analytics
- Ordered Visit → Signup → Search → Add-to-Cart → Checkout → Purchase funnel
- Monthly cohort retention with channel segmentation
- Leakage-safe churn dataset construction using historical feature windows and future labels
- Logistic Regression baseline + XGBoost candidate model
- ROC-AUC, PR-AUC, F1, Brier score and Lift@10%
- Persisted churn scores and model metadata
- Deterministic experiment assignment with SHA-256 bucketing
- Exposure logging, SRM detection, Z-tests, confidence intervals, power analysis and CUPED helper
- React + TypeScript product dashboard
- JWT access tokens + HttpOnly refresh-token rotation
- Rate limiting, strict validation and protected analytics APIs
- Prometheus / Grafana / Sentry / CloudWatch-ready observability
- Docker Compose local environment
- Terraform AWS deployment to ECS Fargate, RDS, ElastiCache, S3 and CloudFront
- GitHub Actions CI/security/deployment workflows

## Architecture

```text
Browser
  |
  v
CloudFront --------------------> private S3 frontend
  |
  | /api/*
  v
Application Load Balancer
  |
  v
ECS Fargate / FastAPI
  |             |             |
  v             v             v
RDS          ElastiCache    S3 model artifacts
PostgreSQL   Redis/Valkey
  |
  +--> SQL analytics
  +--> experiment engine
  +--> churn feature snapshots / scores
```

## Repository phases

See [`docs/PHASES.md`](docs/PHASES.md) for the exact Phase 0 → Phase 8 file mapping.

## Local requirements

- Docker Desktop
- Git
- Python 3.12 (only if running backend outside Docker)
- Node.js 22 (only if running frontend outside Docker)
- AWS CLI v2 and Terraform 1.7+ for AWS deployment

## Phase 0: local bootstrap

```bash
cp .env.example .env
# Set a strong SECRET_KEY before any shared deployment.

docker compose up -d postgres redis
docker compose build
docker compose run --rm backend alembic upgrade head
docker compose up -d backend frontend
```

Open:

- Frontend: http://localhost:8080
- FastAPI docs: http://localhost:8000/docs
- Liveness: http://localhost:8000/api/v1/health/live
- Readiness: http://localhost:8000/api/v1/health/ready
- Prometheus metrics: http://localhost:8000/metrics

## Seed the portfolio dataset

For the first development run use smaller values in `.env`:

```env
GENERATOR_USERS=5000
TARGET_EVENTS=100000
GENERATOR_SEED=42
```

Then:

```bash
docker compose --profile tools run --rm data-generator python seed.py
docker compose --profile tools run --rm data-generator python validate.py
```

After the application is healthy, switch to:

```env
GENERATOR_USERS=50000
TARGET_EVENTS=1200000
GENERATOR_SEED=42
```

and seed again against a clean database.

## Train and score the churn model

```bash
docker compose run --rm backend python -m app.ml.train
docker compose run --rm backend python -m app.jobs.score_churn
```

The training pipeline builds leakage-safe snapshots, compares a Logistic Regression baseline
with XGBoost, stores the selected model artifact, records model metrics in `model_runs`, and the
scoring job persists user-level scores in `churn_scores`.

## Experiment workflow

1. Create an experiment through `/api/v1/experiments`.
2. Eligible users are deterministically assigned using SHA-256 bucketing.
3. Exposure is logged separately from assignment.
4. Outcomes are measured only after exposure and within the configured conversion window.
5. Sample-ratio mismatch is checked before inference.
6. Binary treatment metrics use a two-sided proportions Z-test.
7. The API returns confidence intervals, absolute/relative lift, significance and a decision.

## Security notes

- Access tokens are short-lived and kept in frontend memory.
- Refresh tokens are HttpOnly + SameSite cookies and are rotated/revoked through Redis.
- Passwords use Argon2 via `pwdlib`.
- The event ingestion endpoint uses `X-Event-Ingest-Key` outside local development.
- Event name, time, batch size, revenue and properties payload size are validated.
- Analytics/churn/experiment APIs require authentication.
- SQL uses bound parameters; never interpolate user input into SQL strings.
- AWS stores application secrets in Secrets Manager.
- RDS and ElastiCache are private and accept traffic only from the ECS security group.
- GitHub deployment should use OIDC, not permanent AWS access keys.

See [`SECURITY.md`](SECURITY.md) and [`docs/security/threat-model.md`](docs/security/threat-model.md).

## Test commands

Backend:

```bash
cd backend
pip install -r requirements-dev.txt
ruff check app tests
python -m compileall -q app
pytest -q
bandit -q -r app -x app/ml/artifacts
pip-audit -r requirements.txt
```

Frontend:

```bash
cd frontend
npm install
npm run lint
npm test
npm run build
```

`package-lock.json` is intentionally generated by the first `npm install` in an internet-connected
development environment and should then be committed. The generated source bundle contains all
hand-authored frontend source/configuration files.

## Monitoring

Start the optional local monitoring stack:

```bash
docker compose -f infrastructure/docker-compose.monitoring.yml up -d
```

Prometheus alert rules include API latency/error conditions and the project exposes application
metrics from FastAPI. Grafana provisioning and dashboard JSON are under `monitoring/grafana`.

## AWS deployment

### 1. Authenticate

```bash
aws configure
aws sts get-caller-identity
```

Never share AWS credentials, database passwords or JWT secrets.

### 2. Review and bootstrap infrastructure

> **Cost safety:** This production stack creates chargeable AWS resources and requires real DNS, ACM certificate and remote-state values. Keep `AWS_DEPLOY_ENABLED=false` and do not apply without an approved budget.

```bash
cd infrastructure/terraform
cp backend.hcl.example backend.hcl
terraform init -backend-config=backend.hcl
cp production.tfvars.example terraform.tfvars
terraform fmt -check -recursive
terraform validate
terraform plan -var-file=terraform.tfvars -out=production.tfplan
# Run only after reviewing and approving the saved plan:
# terraform apply production.tfplan
```

The default Terraform configuration keeps the ECS service desired count at `0` so infrastructure
can be created before the first container image exists.

### 3. Push images

Get Terraform outputs:

```bash
terraform output
```

Login to ECR, build and push `backend` and `data-generator` images using the repository URLs from
Terraform outputs.

### 4. Database migration and first data/model run

Run one-off ECS tasks using the generated backend/generator task definitions:

- `alembic upgrade head`
- `python seed.py`
- `python validate.py`
- `python -m app.ml.train`
- `python -m app.jobs.score_churn`

### 5. Start API service

Set:

```hcl
ecs_desired_count = 1
enable_scheduled_jobs = true
```

and apply Terraform again.

### 6. Deploy frontend

```bash
cd frontend
npm install
npm run build
aws s3 sync dist/ s3://<terraform-frontend-bucket> --delete
aws cloudfront create-invalidation --distribution-id <distribution-id> --paths '/*'
```

The CloudFront function rewrites SPA navigation only; `/api/*` errors are never rewritten to
`index.html`.

## Cost-aware portfolio deployment

The default Terraform values intentionally use small single-instance resources for a portfolio
environment. For an enterprise architecture discussion, document the scale-up path rather than
paying for it continuously:

- 2+ ECS tasks across AZs
- RDS Multi-AZ
- ElastiCache replication/failover
- ACM/custom domain
- WAF
- private ECS subnets + NAT/VPC endpoints
- autoscaling and stronger backup/retention policies

## Important engineering choices

- Synthetic data is the primary demo dataset because it provides known retention/channel/treatment
  ground truth.
- Churn labels are defined in a future observation window to prevent target leakage.
- Model preprocessing is persisted with the estimator to prevent training/serving skew.
- A/B assignment and exposure are separate concepts.
- Durable event ingestion uses Redis Streams with consumer groups, retry/recovery, DLQ handling and idempotent PostgreSQL persistence.
- Redis has explicit purposes: token state, rate limiting/cache and durable event-stream processing; PostgreSQL remains the source of truth.
- Kubernetes is intentionally not used; ECS Fargate is sufficient for this portfolio workload.

## License / portfolio use

This repository is intended as a portfolio/reference implementation. Review AWS cost, security,
privacy and compliance requirements before adapting it for real customer data.
