.PHONY: dev down logs migrate seed validate train score test lint build monitoring

dev:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f backend frontend

migrate:
	docker compose run --rm backend alembic upgrade head

seed:
	docker compose run --rm data-generator python seed.py

validate:
	docker compose run --rm data-generator python validate.py

train:
	docker compose run --rm backend python -m app.ml.train

score:
	docker compose run --rm backend python -m app.jobs.score_churn

test:
	docker compose run --rm backend pytest -q

lint:
	docker compose run --rm backend ruff check app tests

build:
	docker compose build

monitoring:
	docker compose -f docker-compose.yml -f infrastructure/docker-compose.monitoring.yml up -d
