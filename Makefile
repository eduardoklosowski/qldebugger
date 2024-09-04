# Project

srcdir = src
testsdir = tests


# Build

.PHONY: build

build:
	poetry build


# Init

.PHONY: init

init:
	poetry install --sync


# Format

.PHONY: fmt

fmt:
	poetry run ruff check --select I001 --fix $(srcdir) $(testsdir)
	poetry run ruff format $(srcdir) $(testsdir)


# Lint

.PHONY: lint lint-poetry lint-ruff-format lint-ruff-check lint-mypy

lint: lint-poetry lint-ruff-format lint-ruff-check lint-mypy

lint-poetry:
	poetry check

lint-ruff-format:
	poetry run ruff format --diff $(srcdir) $(testsdir)

lint-ruff-check:
	poetry run ruff check $(srcdir) $(testsdir)

lint-mypy:
	poetry run mypy --show-error-context --pretty $(srcdir) $(testsdir)


# Tests

.PHONY: test test-pytest

test: test-pytest

test-pytest:
	poetry run pytest --cov=qldebugger --cov-report=term-missing --no-cov-on-fail $(testsdir)


# Docs

.PHONY: docs-build docs-serve

docs-build:
	poetry run mkdocs build

docs-serve:
	poetry run mkdocs serve


# Clean

.PHONY: clean clean-build clean-pycache clean-python-tools clean-docs clean-lock dist-clean

clean: clean-build clean-pycache clean-python-tools clean-docs

clean-build:
	rm -rf dist

clean-pycache:
	find $(srcdir) $(testsdir) -name '__pycache__' -exec rm -rf {} +
	find $(srcdir) $(testsdir) -type d -empty -delete

clean-python-tools:
	rm -rf .ruff_cache .mypy_cache .pytest_cache .coverage .coverage.*

clean-docs:
	rm -rf docs-site

clean-lock:
	rm -rf poetry.lock

dist-clean: clean clean-lock
	rm -rf .venv qldebugger.toml


# Misc

.PHONY: run-aws-mock

run-aws-mock:
	poetry run moto_server -p 4566
