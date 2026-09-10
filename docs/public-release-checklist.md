# Public release checklist

Use this checklist before tagging a release or advertising a live demonstration.

## Source and security

- [ ] Scan the complete Git history with Gitleaks.
- [ ] Confirm `.env*`, private keys, Terraform state, saved plans and cloud credentials are absent.
- [ ] Rotate any credential that was ever committed, even if it was later removed.
- [ ] Confirm model artifacts and datasets contain no customer or confidential information.
- [ ] Review dependency and container scan results.

## Documentation and evidence

- [ ] README claims match current source and automated tests.
- [ ] Screenshots contain only synthetic data and no private infrastructure identifiers.
- [ ] Relative documentation links resolve.
- [ ] Historical benchmark results are labelled as snapshots, not service-level guarantees.
- [ ] Limitations and responsible-use constraints remain visible.

## Deployment

- [ ] HTTPS works from an external network.
- [ ] Liveness and readiness probes pass.
- [ ] Only the public gateway publishes host ports.
- [ ] Backups, recovery steps and cost controls are reviewed for the chosen environment.
- [ ] The live URL is added only after the principal dashboard workflow passes.

## GitHub presentation

- [ ] Apache-2.0 is detected on the repository page.
- [ ] Description, topics and social preview are configured.
- [ ] `main` protection and required checks are enabled.
- [ ] The release PR explains validation, residual risk and rollback.
