# Project

srcdir = qldebugger
testsdir = tests


# Build

.PHONY: build
build:
	poetry build


# Format

.PHONY: fmt fmt-isort fmt-autopep8
fmt: fmt-isort fmt-autopep8

fmt-isort:
	poetry run isort --only-modified $(srcdir) $(testsdir)

fmt-autopep8:
	poetry run autopep8 --in-place $(srcdir) $(testsdir)


# Lint

.PHONY: lint lint-poetry lint-isort lint-autopep8 lint-flake8 lint-mypy lint-bandit
lint: lint-poetry lint-isort lint-autopep8 lint-flake8 lint-mypy lint-bandit

lint-poetry:
	poetry check

lint-isort:
	poetry run isort --check --diff $(srcdir) $(testsdir)

lint-autopep8:
	poetry run autopep8 --diff $(srcdir) $(testsdir)

lint-flake8:
	poetry run flake8 --show-source $(srcdir) $(testsdir)

lint-mypy:
	poetry run mypy --show-error-context --pretty $(srcdir) $(testsdir)

lint-bandit:
	poetry run bandit --silent --recursive $(srcdir)


# Tests

.PHONY: test test-pytest
test: test-pytest

test-pytest:
	poetry run pytest --numprocesses=auto $(testsdir)


# Clean

.PHONY: clean
clean:
	find $(srcdir) $(testsdir) -name '__pycache__' -exec rm -rf {} +
	find $(srcdir) $(testsdir) -type d -empty -delete
	rm -rf poetry.lock dist .mypy_cache .pytest_cache .coverage
