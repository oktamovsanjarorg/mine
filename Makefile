.PHONY: help run dev up down up-prod logs migrate migrate-new test test-unit test-integration lint format clean seed backup locales

help:
	@echo "Available targets:"
	@echo "  run              - Run bot locally"
	@echo "  dev              - Run bot with auto-reload"
	@echo "  up               - Start docker containers (dev)"
	@echo "  down             - Stop docker containers"
	@echo "  up-prod          - Start docker containers (prod)"
	@echo "  logs             - View docker logs"
	@echo "  migrate          - Run alembic migrations"
	@echo "  migrate-new      - Create new alembic migration"
	@echo "  test             - Run all tests"
	@echo "  test-unit        - Run unit tests"
	@echo "  test-integration - Run integration tests"
	@echo "  lint             - Run linters (ruff, mypy)"
	@echo "  format           - Run formatters (ruff format)"
	@echo "  clean            - Clean python cache files"
	@echo "  seed             - Seed database with initial data"
	@echo "  backup           - Backup database"
	@echo "  locales          - Update locales"

run:
	python -m src

dev:
	watchfiles 'python -m src' src/

up:
	docker compose up -d --build

down:
	docker compose down

up-prod:
	docker compose -f docker-compose.prod.yml up -d --build

logs:
	docker compose logs -f

migrate:
	alembic upgrade head

migrate-new:
	@read -p "Migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

test:
	pytest tests/

test-unit:
	pytest tests/unit/

test-integration:
	pytest tests/integration/

lint:
	ruff check src/ tests/
	mypy src/

format:
	ruff format src/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	rm -rf .coverage htmlcov .pytest_cache .mypy_cache .ruff_cache

seed:
	python -m src.scripts.seed

backup:
	docker exec -t sanjar_bot_postgres pg_dumpall -c -U sanjar > dump_`date +%Y-%m-%d"_"%H_%M_%S`.sql

locales:
	pybabel extract -F babel.cfg -o locales/messages.pot .
	pybabel update -d locales -i locales/messages.pot
