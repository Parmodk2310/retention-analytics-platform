# Security policy

## Reporting

Report vulnerabilities privately to the repository owner. Do not open a public issue containing
exploit details, credentials or sensitive logs.

## Repository rules

- Never commit cloud keys, tokens, passwords, environment files, Terraform plans or PII.
- Use local environment files and managed cloud secret stores.
- Use GitHub OIDC instead of permanent deployment credentials.
- Pin third-party Actions and production images to immutable revisions.
- Document scanner exceptions and compensating controls.

## Application controls

The application uses Argon2, short-lived access tokens, HttpOnly refresh rotation, Redis
revocation, rate limits, Pydantic validation, parameterized SQL, bounded pagination and ingest-key
protection. Production data services are private.

These controls do not replace organization-specific penetration testing, privacy review, key
rotation, backup restoration or incident response.

See the [threat model](docs/security/threat-model.md) and
[Terraform security decisions](infrastructure/terraform/SECURITY.md).
