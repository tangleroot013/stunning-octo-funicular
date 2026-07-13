.PHONY: test lint audit clean setup

setup:
	pip install -e ".[dev]"
	pre-commit install

lint:
	ruff check src tests --fix
	black src tests
	mypy src --strict

test:
	pytest --cov=src --cov-report=html --cov-report=term-missing

audit:
	pip-audit --desc

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov dist build *.egg-info

all: lint test audit
