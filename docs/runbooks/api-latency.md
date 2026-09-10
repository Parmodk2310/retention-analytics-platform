# Runbook: High API latency

## Trigger

Investigate when p95 latency breaches the alert threshold, readiness degrades, or users report slow
analytics. Record the affected route, time window, request ID and deployment revision.

## Triage

1. Check whether failures are global or limited to one endpoint.
2. Compare latency, request rate and 5xx signals in Grafana or CloudWatch.
3. Check `/api/v1/health/ready`; separate dependency failure from a slow query.
4. Inspect container CPU, memory and restart counts.
5. Inspect PostgreSQL connections, locks and slow statements.
6. Check Redis latency and event backlog if ingestion or system-health routes are affected.

## Mitigation

- Roll back the last application revision when latency began immediately after deployment.
- Reduce or reject an abusive/unbounded request rather than scaling blindly.
- Restore a missing reviewed index when the query plan confirms regression.
- Scale API tasks only after identifying CPU or concurrency saturation.
- Pause nonessential batch jobs when they compete with interactive database traffic.

## Validation

- readiness is healthy;
- p95 and 5xx return below thresholds for at least two evaluation windows;
- database connections and locks normalize;
- no new event backlog or DLQ growth appears;
- a representative dashboard request completes successfully.

## Escalation evidence

Attach timestamps, request IDs, route, revision, query plan, resource graphs and actions taken.
Never paste access tokens, SQL parameters containing PII or environment secrets.
