.PHONY: setup test lint typecheck docstring check all clean

setup:
	uv sync --all-extras --dev

test:
	PYTHONPATH=. uv run pytest --cov=docvert --cov-report=term-missing --cov-fail-under=100 tests/

lint:
	uv run ruff check .

format:
	uv run ruff check --fix .
	uv run ruff format .

typecheck:
	uv run mypy --strict docvert

docstring:
	uv run interrogate -v -c -I -f 100 docvert

check: lint typecheck docstring test

all: check

clean:
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf out/
