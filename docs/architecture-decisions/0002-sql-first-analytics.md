# ADR 0002: SQL-first analytics
Status: accepted. Core product metrics are computed in PostgreSQL using auditable parameterized SQL instead of Python loops. This mirrors Product Data Scientist workflows and avoids N+1 access patterns.
