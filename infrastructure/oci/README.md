# OCI Live Deployment

This directory deploys RetentionOS as a cost-aware Oracle Cloud demo.
AWS Terraform remains the reference enterprise architecture.

## Target

- Oracle `VM.Standard.A1.Flex` only
- ARM64, 2 OCPUs, 12 GB RAM
- Ubuntu 24.04 LTS and 50 GB boot volume
- Free hostname: `<public-ip-with-dashes>.sslip.io`
- Public ports: TCP 80/443 and UDP 443
- SSH restricted to the administrator IP

Do not replace A1 with a paid `VM.Standard2.*` shape.

## Architecture

Caddy provides HTTPS and proxies the React frontend. FastAPI,
PostgreSQL, Redis and the event worker remain on the private Docker network.

## Deployment

1. Connect: `ssh -i ~/.ssh/id_ed25519 ubuntu@VM_PUBLIC_IP`.
2. Confirm ARM64: `uname -m` must return `aarch64`.
3. Clone this repository and select the deployment branch.
4. Run `sudo ./infrastructure/oci/bootstrap-host.sh ADMIN_IP/32`.
5. Reconnect so Docker group membership takes effect.
6. Copy `.env.production.example` to `.env.production`.
7. Run `chmod 600 .env.production`.
8. Generate secrets with `openssl rand -hex 32`.
9. Set the sslip.io host, ACME email, origins and trusted hosts.
10. Run `./infrastructure/oci/deploy.sh`.

Never commit `.env.production`.

## Verification

- Check services with `docker compose --env-file .env.production -f compose.production.yml ps`.
- Check the frontend at `https://${PUBLIC_HOST}/`.
- Check the API at `https://${PUBLIC_HOST}/api/v1/health/live`.
- Only Caddy should publish host ports.

## Operations

View logs with `docker compose --env-file .env.production -f compose.production.yml logs --tail 200 gateway backend event-worker`.

Update with `git pull --ff-only`, then run the deployment script again.

Stop safely with `docker compose --env-file .env.production -f compose.production.yml stop`.

Never use `docker compose down --volumes` unless permanent data deletion is explicitly intended.
