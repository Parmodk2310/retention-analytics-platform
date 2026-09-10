# ADR 0001: Use a monorepo

- Status: Accepted
- Scope: repository organization and delivery

## Context

The API, frontend, data generator, analytics definitions, ML jobs, monitoring and infrastructure
change together. Splitting them early would require cross-repository version coordination without
independent teams or release cycles.

## Decision

Keep application and infrastructure components in one repository with explicit top-level
boundaries. Review API, schema, UI and deployment changes atomically through one pull request.

## Consequences

Benefits:

- one reproducible local environment;
- contract and consumer changes can land together;
- shared CI and security policies;
- architecture is easy for reviewers to navigate.

Costs:

- CI must avoid rebuilding unrelated components unnecessarily;
- ownership boundaries require CODEOWNERS and directory conventions;
- repository documentation must not become a file-by-file dump.

## Revisit when

Components develop independent teams, access controls, scaling requirements or release cadences
that outweigh atomic review.
