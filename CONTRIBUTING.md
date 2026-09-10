# Contributing

1. Branch from the current default branch.
2. Keep each pull request focused on one reviewable outcome.
3. Add tests for behavioral changes and migrations for schema changes.
4. Run affected backend/frontend checks from the root README.
5. Update contracts, architecture or runbooks when behavior changes.
6. Explain validation, operational risk and rollback in the pull request.

Never commit credentials, environment files, Terraform plans, raw PII or unreviewed generated
artifacts. Keep migrations backward-compatible where practical and use immutable third-party
references in delivery workflows.
