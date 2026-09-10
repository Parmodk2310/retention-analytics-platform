# Implementation phases

This ledger records delivered outcomes and current deployment state. Detailed ownership lives in
the [repository guide](Project_Guide.md).

| Phase | Outcome | Status |
|---|---|---|
| 0 | Monorepo, typed configuration, Compose and health probes | Complete |
| 1 | Synthetic users, events, experiment data and migrations | Complete |
| 2 | SQL-first activity, funnel, cohort, revenue and channel analytics | Complete |
| 3 | React/TypeScript analyst dashboard | Complete |
| 4 | Leakage-safe churn pipeline, artifacts, scores and health | Complete |
| 5 | Assignment, exposure, SRM, inference, power and decisions | Complete |
| 6 | Authentication, validation, limits and security scanning | Complete |
| 7 | Redis Streams reliability, observability and product polish | Complete |
| 8 | Modular AWS Terraform and gated OIDC deployment | Complete, not applied |
| 9 | Cost-aware OCI live-demo deployment | In progress |

## Phase 7 validation snapshot

The Phase 7 freeze recorded 167 backend tests passing with four skipped, eight frontend tests,
clean Gitleaks/pip-audit/npm-audit results, healthy monitoring targets and a 2,000-event benchmark
ending with zero backlog, pending messages and consumer lag. This is historical evidence, not a
permanent guarantee.

## Phase 8 — AWS reference architecture

Delivered VPC/data boundaries, HTTPS ALB, ECS API and worker tasks, ECR, RDS, ElastiCache, private
S3/CloudFront delivery, encrypted model artifacts, alarms, scheduled tasks, OIDC and a gated
production workflow. Terraform formatting/validation, Actionlint, Gitleaks, Trivy, frontend build,
non-root runtime and smoke tests passed.

No Terraform apply occurred. `AWS_DEPLOY_ENABLED=false`; Terraform-generated frontend bucket and
CloudFront distribution variables remain absent.

## Phase 9 — OCI portfolio deployment

Delivered ARM64 CPU-only XGBoost, pinned images, Caddy HTTPS, private Compose networking,
host-hardening/deployment scripts, an operations runbook, a full local production smoke test and a
dedicated OCI NSG.

Pending:

- acquire Singapore `VM.Standard.A1.Flex` capacity;
- bootstrap Ubuntu and configure noncommitted secrets;
- migrate, seed/train/score as required, and start services;
- verify the public HTTPS URL;
- mark pull request #28 ready and merge.

Oracle capacity is an external blocker. Do not substitute a paid shape merely to mark the phase
complete.
