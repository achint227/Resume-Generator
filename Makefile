.PHONY: install dev run lint format test clean

install:
	uv sync

dev:
	uv run python app.py

run:
	uv run python app.py

lint:
	uv run ruff check .

format:
	uv run black .

test:
	uv run pytest

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .ruff_cache
