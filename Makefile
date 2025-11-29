.PHONY: install dev run lint format test clean docker-build docker-run typecheck

install:
	uv sync

install-mongodb:
	uv sync --extra mongodb

dev:
	FLASK_DEBUG=true uv run python app.py

run:
	uv run python app.py

lint:
	uv run ruff check .

format:
	uv run black .
	uv run ruff check --fix .

typecheck:
	uv run mypy src/

test:
	uv run pytest

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf output/*.pdf output/*.tex output/*.aux output/*.log

docker-build:
	docker build -t resume-generator .

docker-run:
	docker run -p 8000:8000 resume-generator
