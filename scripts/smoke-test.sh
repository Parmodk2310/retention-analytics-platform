#!/usr/bin/env bash
set -euo pipefail
curl -fsS http://localhost:8000/api/v1/health/live
curl -fsS http://localhost:8000/api/v1/health/ready
curl -fsS http://localhost:8080/ >/dev/null
echo "smoke tests passed"
