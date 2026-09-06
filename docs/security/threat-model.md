# Threat Model

Assets: dashboard accounts, tokens, behavioral data, experiment integrity, model artifacts, AWS credentials.

Controls include Argon2 password hashing, short access tokens, HttpOnly refresh cookies, refresh-token revocation in Redis, login throttling, parameterized SQL, Pydantic validation, event allowlists, bounded pagination, TLS in production, private RDS/Redis subnets, IAM roles instead of long-lived AWS keys, secret scanning, dependency scanning, container scanning, and S3 Block Public Access.

Never put AWS access keys, database passwords, JWT secrets, or customer PII in the repository.
