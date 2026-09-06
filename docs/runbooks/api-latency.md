# Runbook: High API latency
1. Check p95 and 5xx in Grafana/CloudWatch. 2. Inspect RDS connections and slow SQL. 3. Confirm event-date indexes are present. 4. Scale ECS tasks if CPU constrained. 5. Roll back the last release if regression is code-related.
