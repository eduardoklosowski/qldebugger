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
	poetry run autopep8 --recursive --in-place $(srcdir) $(testsdir)
	poetry run ruff --fix $(srcdir) $(testsdir)


# Lint

.PHONY: lint lint-poetry lint-pycodestyle lint-autopep8 lint-ruff lint-mypy

lint: lint-poetry lint-pycodestyle lint-autopep8 lint-ruff lint-mypy

lint-poetry:
	poetry check

lint-pycodestyle:
	poetry run pycodestyle --show-source $(srcdir) $(testsdir)

lint-autopep8:
	poetry run autopep8 --diff --exit-code --recursive $(srcdir) $(testsdir)

lint-ruff:
	poetry run ruff check --show-source $(srcdir) $(testsdir)

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
