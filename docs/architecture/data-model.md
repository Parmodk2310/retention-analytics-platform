# Data Model

- `accounts`: dashboard authentication identities; kept separate from analytical users.
- `users`: simulated product users and acquisition attributes.
- `events`: append-only behavioral event log with UTC timestamps and JSONB properties.
- `experiments`: experiment metadata and allocation.
- `experiment_assignments`: deterministic user/variant mapping.
- `experiment_exposures`: actual treatment exposure; metrics are measured after this timestamp.
- `model_runs`: immutable model metadata and evaluation metrics.
- `churn_scores`: daily user-level risk score, model version, and reason codes.

The separation between assignment and exposure prevents users who were assigned but never saw the treatment from contaminating exposure-based analysis.
