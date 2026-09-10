#!/usr/bin/env bash
set -Eeuo pipefail

REPOSITORY_ROOT="$(
  cd "$(dirname "${BASH_SOURCE[0]}")/../.." &&
    pwd
)"

cd "$REPOSITORY_ROOT"

COMPOSE_FILE="compose.production.yml"
ENV_FILE=".env.production"
MODEL_FILE="backend/app/ml/artifacts/churn_model.joblib"
METADATA_FILE="backend/app/ml/artifacts/model_metadata.json"

compose() {
  docker compose \
    --env-file "$ENV_FILE" \
    -f "$COMPOSE_FILE" \
    "$@"
}

echo "===== VERIFY DEPLOYMENT FILES ====="

for FILE in \
  "$COMPOSE_FILE" \
  "$ENV_FILE" \
  "$MODEL_FILE" \
  "$METADATA_FILE" \
  infrastructure/oci/Caddyfile; do
  if ! test -s "$FILE"; then
    echo "ERROR: required file is missing or empty: $FILE"
    exit 1
  fi
done

chmod 600 "$ENV_FILE"

echo "PASS: deployment files exist"
echo "PASS: production environment permissions restricted"

echo
echo "===== VERIFY NO PLACEHOLDERS ====="

if grep -nE \
    'REPLACE_WITH|example\.com|YOUR_|CHANGE_ME' \
    "$ENV_FILE"; then
  echo "ERROR: production environment contains placeholders"
  exit 1
fi

echo "PASS: no environment placeholders remain"

echo
echo "===== READ PUBLIC HOST ====="

PUBLIC_HOST="$(
  awk -F= '
    $1 == "PUBLIC_HOST" {
      sub(/^[^=]*=/, "")
      print
      exit
    }
  ' "$ENV_FILE"
)"

test -n "$PUBLIC_HOST"

if ! printf '%s\n' "$PUBLIC_HOST" |
    grep -Eq '^[A-Za-z0-9.-]+$'; then
  echo "ERROR: PUBLIC_HOST is invalid"
  exit 1
fi

echo "Public host: $PUBLIC_HOST"

echo
echo "===== VERIFY DOCKER ====="

docker --version
docker compose version

echo
echo "===== VALIDATE COMPOSE MODEL ====="

compose config --quiet
echo "PASS: production Compose configuration is valid"

echo
echo "===== PULL PINNED SERVICE IMAGES ====="

compose pull postgres redis gateway

echo
echo "===== BUILD APPLICATION IMAGES ====="

compose build backend event-worker frontend

echo
echo "===== START DATABASE AND REDIS ====="

compose up \
  --detach \
  --wait \
  --wait-timeout 180 \
  postgres \
  redis

echo "PASS: PostgreSQL and Redis are healthy"

echo
echo "===== RUN DATABASE MIGRATIONS ====="

compose run \
  --rm \
  backend \
  alembic upgrade head

echo "PASS: database migrations completed"

echo
echo "===== START PRODUCTION APPLICATION ====="

compose up \
  --detach \
  --wait \
  --wait-timeout 300 \
  backend \
  event-worker \
  frontend \
  gateway

echo "PASS: production services started"

echo
echo "===== VERIFY SERVICE STATE ====="

compose ps

RUNNING_SERVICES="$(
  compose ps \
    --services \
    --status running |
    sort
)"

EXPECTED_SERVICES="$(
  printf '%s\n' \
    backend \
    event-worker \
    frontend \
    gateway \
    postgres \
    redis |
    sort
)"

if test "$RUNNING_SERVICES" != "$EXPECTED_SERVICES"; then
  echo "ERROR: production service set is incomplete"
  echo "Expected:"
  printf '%s\n' "$EXPECTED_SERVICES"
  echo "Running:"
  printf '%s\n' "$RUNNING_SERVICES"
  exit 1
fi

echo "PASS: exactly six production services are running"

echo
echo "===== VERIFY PUBLIC HTTPS ENDPOINT ====="

HEALTH_URL="https://${PUBLIC_HOST}/api/v1/health/live"
FRONTEND_URL="https://${PUBLIC_HOST}/"

HEALTH_READY=false

for ATTEMPT in $(seq 1 24); do
  if curl \
      --fail \
      --silent \
      --show-error \
      --max-time 15 \
      "$HEALTH_URL" \
      >/dev/null; then
    HEALTH_READY=true
    break
  fi

  echo "HTTPS attempt $ATTEMPT/24 not ready"
  sleep 5
done

if test "$HEALTH_READY" != "true"; then
  echo "ERROR: public HTTPS health endpoint did not become ready"
  compose logs --tail 100 gateway backend
  exit 1
fi

curl \
  --fail \
  --silent \
  --show-error \
  --max-time 15 \
  "$FRONTEND_URL" \
  >/dev/null

echo "PASS: backend HTTPS health endpoint responds"
echo "PASS: frontend HTTPS page responds"

echo
echo "===== DEPLOYMENT COMPLETE ====="
echo "Live URL: $FRONTEND_URL"
