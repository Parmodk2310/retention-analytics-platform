# Retention Analytics Platform — Complete File Operations Guide

## 1. Project Root

| File | Purpose | Why We Use It |
|------|---------|---------------|
| `.env.example` | Template for environment variables | Secrets never committed to Git. Team members copy to `.env` and fill in local values. |
| `.gitignore` | Excludes files from version control | Prevents `.env`, `__pycache__`, `node_modules`, and model artifacts from being committed. |
| `docker-compose.yml` | Local development orchestration | Spins up PostgreSQL, Redis, backend, and frontend with one command. Ensures consistent local environments across team members. |
| `docker-compose.monitoring.yml` | Observability stack | Adds Prometheus, Grafana, Alertmanager for local monitoring. Separated from main compose to keep it optional. |
| `Makefile` | Common command shortcuts | `make dev`, `make test`, `make deploy` abstract complex Docker/CLI commands. Reduces onboarding friction. |
| `railway.toml` | Railway deployment configuration | Zero-config deploy to Railway.app. Defines build command, health checks, and restart policy. |
| `README.md` | Project documentation | Onboarding guide for new developers. Explains setup, architecture, and deployment. |

---

## 2. Backend (`backend/`)

### 2.1 Configuration & Entry Point

| File | Purpose | Operation |
|------|---------|-----------|
| `app/config.py` | Pydantic Settings | Loads env vars with type validation. `settings.DATABASE_URL` is used everywhere. Change `.env` → no code changes needed. |
| `app/main.py` | FastAPI app factory | Creates the FastAPI instance, registers middleware, routes, and lifespan hooks. `lifespan()` loads the ML model at startup and closes DB connections on shutdown. |

### 2.2 Core (`app/core/`)

| File | Purpose | Operation |
|------|---------|-----------|
| `security.py` | JWT auth utilities | `create_access_token()` encodes user_id into JWT. `get_current_user()` dependency validates Bearer tokens on every protected route. bcrypt hashes passwords with salt. |
| `middleware.py` | Request interceptors | `RequestTimingMiddleware` logs method, path, status, and duration for every request. Adds `X-Request-ID` header for distributed tracing. `ErrorHandlingMiddleware` catches unhandled exceptions and returns JSON error responses (prevents stack trace leaks). |
| `exceptions.py` | Custom API exceptions | `NotFoundException`, `ValidationException` provide consistent error format with machine-readable `code` field. Frontend uses `code` to show appropriate toast notifications. |
| `logging.py` | Structured JSON logging | `JSONFormatter` outputs logs as JSON for ELK/Grafana Loki ingestion. Includes `request_id`, `user_id`, and `duration_ms` for traceability. |

### 2.3 Database (`app/db/`)

| File | Purpose | Operation |
|------|---------|-----------|
| `base.py` | SQLAlchemy engine & session | Creates `QueuePool` connection pool (reuses DB connections). `pool_pre_ping=True` verifies connections before use (handles DB restarts gracefully). |
| `models/user.py` | User dimension table | Stores signup_date, acquisition_channel, device_type. `events` relationship enables `user.events` lazy loading. |
| `models/event.py` | Events fact table | Stores 1M+ events. `properties` is JSONB for flexible metadata. Indexed on `(user_id, timestamp)` and `(event_type, timestamp)` for fast analytics queries. |
| `models/session.py` | Session aggregation | Pre-aggregated session metrics (duration, page_views). Reduces ML feature computation time. |
| `models/experiment.py` | Experiment metadata | `Experiment` table stores hypothesis and status. `ExperimentAssignment` stores variant assignments with unique constraint on `(experiment_id, user_id)`. |
| `repositories/user_repo.py` | User data access | Repository pattern abstraction. `get_by_id()`, `get_by_channel()` methods encapsulate query logic for testability. |
| `repositories/event_repo.py` | Event data access | `get_events_for_user()`, `get_events_by_type()` provide clean interfaces for complex filtered queries. |

### 2.4 API (`app/api/`)

| File | Purpose | Operation |
|------|---------|-----------|
| `deps.py` | Dependency injection | `get_db()` yields a DB session that auto-closes. `get_current_user_id()` injects authenticated user ID into routes via FastAPI's `Depends()`. |
| `router.py` | Route aggregation | Collects all v1 routers under `/api/v1` prefix. Enables API versioning (future `/api/v2/`). |
| `v1/health.py` | Health probes | `/health/` returns 200 for load balancer health checks. `/ready` verifies DB connectivity before accepting traffic (used by Kubernetes). |
| `v1/auth.py` | Authentication | `/auth/login` accepts OAuth2 password flow, returns JWT access + refresh tokens. `/auth/refresh` exchanges refresh token for new access token. |
| `v1/analytics.py` | Analytics endpoints | `/analytics/metrics` → DAU/WAU/MAU. `/analytics/funnel` → 6-stage conversion. `/analytics/cohorts/retention` → retention matrix. All use `AnalyticsService`. |
| `v1/experiments.py` | A/B test endpoints | `/experiments/{id}/assign/{user_id}` → deterministic hash assignment. `/experiments/{id}/results` → Z-test statistical analysis. |
| `v1/ml.py` | ML endpoints | `/ml/churn/predict` → batch churn prediction. `/ml/churn/user/{id}` → single user prediction. Loads XGBoost model at startup. |

### 2.5 Services (`app/services/`)

| File | Purpose | Operation |
|------|---------|-----------|
| `analytics_service.py` | SQL analytics engine | Contains all raw SQL queries using CTEs and window functions. `get_cohort_retention()` self-joins users with events by month. `get_funnel_analysis()` uses CASE-based aggregation. |
| `funnel_service.py` | Funnel analysis | `get_channel_funnel()` compares conversion rates across acquisition channels. Enables channel optimization decisions. |
| `cohort_service.py` | Cohort analysis | `get_channel_retention()` pivots retention data by channel. Used for "which channel has best retention?" insights. |
| `experiment_service.py` | Experiment lifecycle | `calculate_sample_size()` runs power analysis before experiment launch. `conclude_experiment()` archives results and stops data collection. |

### 2.6 Experiments Engine (`app/experiments/`)

| File | Purpose | Operation |
|------|---------|-----------|
| `stats.py` | Statistical tests | `ABTestAnalyzer.analyze_proportions()` runs Z-test via `statsmodels`. Returns p-value, confidence intervals, and power. `required_sample_size()` uses `NormalIndPower` for pre-experiment planning. |
| `randomizer.py` | Hash-based assignment | `assign_variant()` uses MD5 hash of `experiment_id:user_id` to deterministically assign variants. Same inputs always produce same output. No DB lookup required. |
| `metrics.py` | Metric computation | `compute_proportion_metric()` counts conversions per variant. Supports custom event types (purchase, signup, etc.). |
| `reporter.py` | Report generation | `generate_summary()` creates markdown reports with statistical results for stakeholder communication. |

### 2.7 ML Pipeline (`app/ml/`)

| File | Purpose | Operation |
|------|---------|-----------|
| `features.py` | Feature engineering | `RFMFeatureEngineer` transforms raw user data into Recency, Frequency, Monetary + engagement features. sklearn transformer interface enables pipeline composition. |
| `train.py` | Model training | `ChurnModelTrainer` fetches data from PostgreSQL, engineers features, trains 3 models (XGBoost, Random Forest, Logistic Regression), evaluates with 5-fold CV, saves best model as joblib artifact. |
| `predict.py` | Inference service | `ChurnPredictor` loads model artifact at startup. `predict()` fetches user features from DB, engineers them identically to training, returns sorted risk scores. Singleton pattern ensures one model instance. |
| `evaluate.py` | Model evaluation | `evaluate_model()` computes AUC-ROC, precision, recall, F1, and confusion matrix. Used for model monitoring and drift detection. |
| `artifacts/churn_xgb_v1.joblib` | Serialized model | Contains trained model + feature columns + metadata. Versioned filename enables rollback if new model degrades. |

### 2.8 Analytics SQL (`app/analytics/`)

| File | Purpose | Operation |
|------|---------|-----------|
| `queries/retention.sql` | Cohort retention query | Self-join pattern with `DATE_TRUNC('month', ...)` groups users by signup month and counts retained users per period. |
| `queries/funnel.sql` | Funnel query | `CASE WHEN` aggregation with `MAX()` handles multiple events per user. Computes drop-off between each stage. |
| `queries/metrics.sql` | DAU/WAU/MAU query | Conditional `COUNT(DISTINCT)` in single pass. Computes stickiness as `DAU/MAU` ratio. |
| `executor.py` | SQL runner | `execute_query()` loads SQL files and renders them with Jinja2 templating. Separates SQL from Python code. |

### 2.9 Schemas (`app/schemas/`)

| File | Purpose | Operation |
|------|---------|-----------|
| `user.py` | User Pydantic models | `UserCreate` validates incoming data. `UserResponse` defines API output shape. `from_attributes=True` enables ORM mode. |
| `analytics.py` | Analytics Pydantic models | `FunnelResponse`, `CohortResponse` type the API responses. Frontend TypeScript types can be auto-generated from these. |
| `experiment.py` | Experiment Pydantic models | `ExperimentCreate` validates `metric_type` against allowed values. `ABTestAnalysis` structures statistical results. |

### 2.10 Tests (`tests/`)

| File | Purpose | Operation |
|------|---------|-----------|
| `conftest.py` | Pytest fixtures | `db_engine` creates in-memory SQLite. `db_session` provides isolated transactions (rolled back after each test). `client` provides HTTP test client. |
| `unit/test_experiments.py` | Stats unit tests | Verifies Z-test produces significant results for known data (324/1000 vs 365/1000). Verifies sample size calculations return reasonable values. |
| `unit/test_randomizer.py` | Randomizer tests | Verifies deterministic assignment (same input → same output). Verifies even distribution across 10,000 assignments. |

---

## 3. Data Generator (`data-generator/`)

| File | Purpose | Operation |
|------|---------|-----------|
| `seed.py` | Synthetic data generation | Generates 50K users with channel-biased retention and 1.2M events with realistic funnel drop-offs. Uses NumPy vectorization for speed. Seeds database via SQLAlchemy bulk insert. |
| `Dockerfile` | Generator container | Standalone container for data seeding. Runs once via `docker compose --profile seed up`. |

---

## 4. Frontend (`frontend/`)

### 4.1 Config

| File | Purpose | Operation |
|------|---------|-----------|
| `package.json` | Node dependencies | React 18, TypeScript, Vite, TanStack Query, Recharts, Tailwind, Zustand, Axios. |
| `vite.config.ts` | Build tool config | Path alias `@/` → `./src/`. Proxy `/api` to `localhost:8000` for dev. Code splitting into vendor/charts/query chunks. |
| `tsconfig.json` | TypeScript config | Strict mode enabled. Path mapping for clean imports. |
| `tailwind.config.js` | Design tokens | Custom color palette (CSS variables), border radius, font family. Dark mode via `class` strategy. |

### 4.2 Core

| File | Purpose | Operation |
|------|---------|-----------|
| `src/main.tsx` | Entry point | Creates React root, wraps app in QueryClientProvider and BrowserRouter. |
| `src/App.tsx` | Root component | Layout shell with Sidebar, Header, and Routes. |
| `src/index.css` | Global styles | Tailwind directives, CSS variables for theming, custom scrollbar, heatmap hover effects, skeleton shimmer animation. |
| `src/lib/utils.ts` | Utility functions | `cn()` merges Tailwind classes with `tailwind-merge` (prevents class conflicts). |
| `src/lib/formatters.ts` | Data formatters | `formatNumber()`, `formatPercent()`, `formatCurrency()`, `formatDate()`, `formatDuration()`. Centralized formatting for consistency. |
| `src/lib/constants.ts` | App constants | Risk thresholds, funnel stage names, channel colors. Changing a threshold here updates the entire UI. |

### 4.3 State Management

| File | Purpose | Operation |
|------|---------|-----------|
| `src/store/authStore.ts` | Auth state (Zustand) | Stores JWT token in memory + localStorage. `isAuthenticated` derived from token presence. `logout()` clears everything. |
| `src/store/uiStore.ts` | UI state (Zustand) | Sidebar collapse state, theme preference, toast notifications. Lightweight alternative to Redux. |

### 4.4 API Layer

| File | Purpose | Operation |
|------|---------|-----------|
| `src/services/api.ts` | Axios instance | Base URL, request interceptor adds JWT header, response interceptor handles 401 redirects. |
| `src/services/analyticsApi.ts` | Analytics API client | Typed methods for metrics, funnel, cohorts, revenue endpoints. Uses TanStack Query keys for caching. |
| `src/services/experimentApi.ts` | Experiment API client | `getResults()`, `assignVariant()` methods with proper TypeScript return types. |

### 4.5 Hooks

| File | Purpose | Operation |
|------|---------|-----------|
| `src/hooks/useAnalytics.ts` | Analytics data fetching | `useMetrics()`, `useFunnel()`, `useCohortRetention()` wrap TanStack Query with 5-minute stale time. |
| `src/hooks/useAuth.ts` | Auth operations | `useLogin()`, `useLogout()` mutations. Handles token storage and cache invalidation. |
| `src/hooks/useExperiments.ts` | Experiment data | `useExperimentResults()` fetches and caches A/B test analysis. |

### 4.6 Types

| File | Purpose | Operation |
|------|---------|-----------|
| `src/types/analytics.d.ts` | Analytics TypeScript types | Interfaces for API responses: `MetricsResponse`, `FunnelStage`, `CohortResponse`, `ChurnPrediction`. |
| `src/types/experiment.d.ts` | Experiment TypeScript types | `ExperimentResult`, `ABTestAnalysis` interfaces ensure type safety across frontend. |

### 4.7 Components

| File | Purpose | Operation |
|------|---------|-----------|
| `components/layout/Sidebar.tsx` | Navigation sidebar | Responsive sidebar with nav links, active state styling, system status indicator. |
| `components/layout/Header.tsx` | Top bar | Search input, notification bell with unread indicator, user profile dropdown. |
| `components/ui/Skeleton.tsx` | Loading placeholder | `animate-pulse` div with configurable dimensions. Matches content shape to reduce layout shift. |
| `components/charts/MetricCard.tsx` | KPI card | Displays value, trend arrow, and percentage change. Color-coded for positive/negative trends. |
| `components/charts/RetentionHeatmap.tsx` | Cohort heatmap | Grid of colored cells representing retention rates. Hover tooltip shows exact percentage. Legend for color scale. |
| `components/charts/FunnelChart.tsx` | Funnel visualization | Horizontal bar chart via Recharts. Shows users per stage and drop-off percentages. |
| `components/charts/MetricSparkline.tsx` | Mini trend chart | Small line chart for dashboard cards. Shows 7-day trend without axis labels. |

### 4.8 Pages

| File | Purpose | Operation |
|------|---------|-----------|
| `pages/Dashboard.tsx` | Main dashboard | 4 KPI cards + retention heatmap + funnel chart. Uses `useMetrics`, `useFunnel`, `useCohortRetention` hooks. Shows skeleton loaders during data fetch. |
| `pages/CohortAnalysis.tsx` | Cohort deep dive | Full-page retention heatmap + channel comparison cards. Best/worst channel identification. |
| `pages/FunnelAnalysis.tsx` | Funnel diagnostics | Funnel chart + critical insight alert card. Identifies highest drop-off stage with recommendation. |
| `pages/ChurnPrediction.tsx` | ML predictions | Summary cards (total scored, high risk, at-risk revenue) + sortable predictions table with risk level badges and probability bars. |
| `pages/Experiments.tsx` | A/B test results | Control vs Treatment comparison cards. Statistical metrics (lift, p-value, power, significance). Recommendation banner with color coding. |
| `pages/Settings.tsx` | App settings | Theme toggle, notification preferences, API key management. |

---

## 5. Infrastructure

### 5.1 Docker

| File | Purpose | Operation |
|------|---------|-----------|
| `backend/Dockerfile` | Backend container | Multi-stage build: deps → runtime. Non-root user for security. Gunicorn with Uvicorn workers for production ASGI serving. |
| `frontend/Dockerfile` | Frontend container | Multi-stage: Node build → Nginx serve. Security headers (X-Frame-Options, CSP). Gzip compression. |
| `data-generator/Dockerfile` | Seed container | Runs `seed.py` once and exits. Used with Docker Compose profiles. |
| `frontend/nginx.conf` | Frontend reverse proxy | Proxies `/api/` to FastAPI, serves production assets with caching, and provides the React Router SPA fallback. |

### 5.2 Terraform (AWS)

| File | Purpose | Operation |
|------|---------|-----------|
| `infrastructure/terraform/main.tf` | AWS infrastructure | VPC, ECS Fargate, RDS PostgreSQL, ElastiCache Redis, ALB, Route53, ACM SSL. Auto-scaling based on CPU/memory. |
| `infrastructure/terraform/variables.tf` | Input variables | Environment-specific values (instance sizes, domain name, secrets). Validated with constraints. |
| `infrastructure/terraform/iam.tf` | IAM roles | ECS task execution role, task role, RDS monitoring role. Least-privilege permissions. |
| `infrastructure/terraform/outputs.tf` | Output values | ALB DNS, RDS endpoint, Redis endpoint, ECR URL. Displayed after `terraform apply`. |

### 5.3 CI/CD

| File | Purpose | Operation |
|------|---------|-----------|
| `.github/workflows/ci-backend.yml` | Backend CI | Runs on PR/push. Steps: lint (flake8), type check (mypy), security scan (bandit), unit tests (pytest), coverage upload (Codecov). |
| `.github/workflows/ci-frontend.yml` | Frontend CI | Runs on PR/push. Steps: `npm ci`, `npm run lint`, TypeScript check, production build. |
| `.github/workflows/deploy-aws.yml` | AWS deployment | Triggered on main branch merge. Builds Docker image, pushes to ECR, updates ECS task definition, deploys service. |
| `.github/workflows/deploy-railway.yml` | Railway deployment | Triggered on main branch. Uses Railway CLI for zero-downtime deploy. |

### 5.4 Monitoring

| File | Purpose | Operation |
|------|---------|-----------|
| `monitoring/prometheus/prometheus.yml` | Scraping config | Defines targets: backend `/metrics`, node-exporter, postgres-exporter, redis-exporter. 15s scrape interval. |
| `monitoring/prometheus/rules/alerts.yml` | Alert rules | Critical alerts: HighErrorRate (&gt;5%), HighLatency (&gt;500ms), ModelDegradation (AUC&lt;0.75), ServiceDown. |
| `monitoring/alertmanager/config.yml` | Alert routing | Routes critical alerts to PagerDuty, warnings to Slack. Email fallback for all alerts. |
| `monitoring/grafana/provisioning/datasources/datasources.yml` | Data source config | Auto-registers Prometheus as default data source on Grafana startup. |
| `monitoring/grafana/provisioning/dashboards/dashboards.yml` | Dashboard provider | Auto-loads dashboard JSON files from `/var/lib/grafana/dashboards`. |
| `monitoring/grafana/dashboards/overview.json` | Main dashboard | Availability, request rate, latency percentiles (p50/p95/p99), active users, revenue by channel. |

---

## 6. Operations Runbook

### Local Development
```bash
make reset          # Full reset: DB + seed + train
make dev            # Start backend
make dev-front      # Start frontend