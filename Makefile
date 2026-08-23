.PHONY: install dev seed migrate train build up down test

# Development
install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

dev:
	docker compose up -d postgres redis
	cd backend && uvicorn app.main:app --reload &

dev-front:
	cd frontend && npm run dev

# Database
migrate:
	cd backend && alembic upgrade head

seed:
	docker compose --profile seed up data-generator

# ML
train:
	cd backend && python -m app.ml.train

# Docker
up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

# Testing
test-back:
	cd backend && pytest -v

test-front:
	cd frontend && npm test

# Full reset
reset:
	docker compose down -v
	docker compose up -d postgres redis
	sleep 3
	cd backend && alembic upgrade head
	docker compose --profile seed up data-generator
	cd backend && python -m app.ml.train