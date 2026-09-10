# ADR 0002: Keep core analytics SQL-first

- Status: Accepted
- Scope: product metric computation

## Context

Retention, funnel and activity metrics must be auditable by analysts and efficient over relational
event data. Python loops and ORM object traversal obscure definitions and encourage N+1 access.

## Decision

Implement core product metrics as parameterized PostgreSQL queries. Keep SQL definitions separate
from transport and presentation logic; use Python services to validate inputs, execute queries and
shape typed responses.

## Consequences

Benefits:

- metric definitions are directly reviewable;
- database query planning and indexes can be inspected;
- bounded queries avoid transferring raw event histories to Python;
- behavior resembles product analytics practice.

Costs:

- PostgreSQL-specific SQL reduces database portability;
- SQL requires dedicated tests and query-plan review;
- semantic changes must be versioned carefully because several dashboards may share a metric.

## Guardrails

- Bind all user inputs; never interpolate request values into SQL text.
- Require explicit date bounds.
- Test ordering rules for funnels and UTC boundaries for cohorts.
- Promote repeated or expensive queries to reviewed aggregates only after measurement.

## Revisit when

Data volume or workload isolation justifies a warehouse or semantic layer. Preserve metric-contract
tests during any migration.
