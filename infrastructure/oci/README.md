# OCI Portfolio Deployment

This directory contains the deployment path for a cost-aware Oracle Cloud demo. The configuration
is validated, but the service is not live until the verification section succeeds against a real
public URL. AWS Terraform remains the reference enterprise architecture.

## Target

- Oracle `VM.Standard.A1.Flex` only
- ARM64, 2 OCPUs, 12 GB RAM
- Ubuntu 24.04 LTS and 50 GB boot volume
- Free hostname: `<public-ip-with-dashes>.sslip.io`
- Public ports: TCP 80/443 and UDP 443
- SSH restricted to the administrator IP

Singapore A1 capacity is currently the external blocker. Do not replace A1 with a paid
`VM.Standard2.*` shape merely to complete the demo.

## Architecture

Caddy provides HTTPS and proxies the React frontend. FastAPI,
PostgreSQL, Redis and the event worker remain on the private Docker network.

## Deployment

1. Confirm the instance is `RUNNING`, attached to the dedicated NSG and assigned a public IP.
2. Connect: `ssh -i ~/.ssh/id_ed25519 ubuntu@VM_PUBLIC_IP`.
3. Confirm ARM64: `uname -m` must return `aarch64`.
4. Clone this repository and select the deployment branch.
5. Run `sudo ./infrastructure/oci/bootstrap-host.sh ADMIN_IP/32`.
6. Reconnect so Docker group membership takes effect.
7. Copy `.env.production.example` to `.env.production`.
8. Run `chmod 600 .env.production`.
9. Generate secrets with `openssl rand -hex 32`.
10. Set the sslip.io host, ACME email, origins and trusted hosts.
11. Run `./infrastructure/oci/deploy.sh`.

Never commit `.env.production`.

## Verification

- Check services with `docker compose --env-file .env.production -f compose.production.yml ps`.
- Check the frontend at `https://${PUBLIC_HOST}/`.
- Check the API at `https://${PUBLIC_HOST}/api/v1/health/live`.
- Only Caddy should publish host ports.

Record a live URL in the root README only after HTTPS, the API probe and the primary dashboard
workflow all pass from a separate internet connection.

## Operations

View logs with `docker compose --env-file .env.production -f compose.production.yml logs --tail 200 gateway backend event-worker`.

Update with `git pull --ff-only`, then run the deployment script again.

Stop safely with `docker compose --env-file .env.production -f compose.production.yml stop`.

Never use `docker compose down --volumes` unless permanent data deletion is explicitly intended.
