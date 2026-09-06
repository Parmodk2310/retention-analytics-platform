#!/usr/bin/env bash
set -euo pipefail
cp -n .env.example .env || true
python - <<'PY2'
from pathlib import Path
p=Path('.env')
s=p.read_text();
if 'change-me-with-openssl-rand-hex-32' in s:
    import secrets;s=s.replace('change-me-with-openssl-rand-hex-32',secrets.token_hex(32));p.write_text(s)
PY2
docker compose up -d postgres redis
docker compose build backend frontend data-generator
docker compose run --rm backend alembic upgrade head
echo "Bootstrap complete. Run: docker compose up backend frontend"
