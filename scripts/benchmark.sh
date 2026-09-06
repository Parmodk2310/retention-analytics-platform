#!/usr/bin/env bash
set -euo pipefail
URL=${1:-http://localhost:8000/api/v1/health/live}
if command -v hey >/dev/null; then hey -n 1000 -c 20 "$URL"; else echo "Install hey for load testing: https://github.com/rakyll/hey"; fi
