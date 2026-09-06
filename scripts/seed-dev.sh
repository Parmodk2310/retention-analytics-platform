#!/usr/bin/env bash
set -euo pipefail
docker compose run --rm data-generator python seed.py
docker compose run --rm data-generator python validate.py
