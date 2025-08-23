# TungShing Project Makefile
.PHONY: help install install-dev test lint type-check format clean build publish check all

# Default target
help:  ## Show this help message
	@echo "TungShing Project - Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install the package
	pip install .

install-dev:  ## Install development dependencies
	pip install -e .[dev]

test:  ## Run tests
	pytest -v

lint:  ## Run linter
	ruff check src tests
	ruff format --check src tests

type-check:  ## Run type checker
	mypy src --ignore-missing-imports

format:  ## Format code
	ruff format src tests
	ruff check --fix src tests

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build:  ## Build package
	python -m build

publish:  ## Publish to PyPI (requires TWINE_PASSWORD)
	python -m twine upload dist/*

check:  ## Run all checks (lint, type, test)
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) test

all: clean install-dev check build  ## Run complete workflow

# Development commands
pre-commit-install:  ## Install pre-commit hooks
	pre-commit install

pre-commit-run:  ## Run pre-commit on all files
	pre-commit run --all-files

version:  ## Show current version
	@python -c "exec(open('src/tungshing/_version.py').read()); print(__version__)"

# CI-friendly commands  
ci-install:  ## Install for CI
	pip install --upgrade pip
	pip install build twine
	pip install -e .[dev]

ci-test:  ## Run tests for CI
	pytest -v --tb=short

ci-build:  ## Build for CI
	python -m build
	python -m twine check dist/*