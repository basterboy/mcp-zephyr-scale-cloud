# Makefile for MCP Zephyr Scale Cloud

.PHONY: help install test test-unit test-integration test-fast test-coverage clean lint format type-check ci

# Default target
help:
	@echo "🧪 MCP Zephyr Scale Cloud - Development Commands"
	@echo "================================================"
	@echo ""
	@echo "Setup:"
	@echo "  install       Install dependencies with Poetry"
	@echo "  install-dev   Install with development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  test          Run all tests"
	@echo "  test-unit     Run unit tests only"
	@echo "  test-integration  Run integration tests only"
	@echo "  test-fast     Run tests without coverage (faster)"
	@echo "  test-coverage Run tests with detailed coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint          Run all linting checks"
	@echo "  format        Format code with black and isort"
	@echo "  type-check    Run mypy type checking"
	@echo ""
	@echo "CI/CD:"
	@echo "  ci            Run complete CI pipeline locally"
	@echo "  clean         Clean up test artifacts"

# Installation
install:
	poetry install

install-dev:
	poetry install --with dev

# Testing
test:
	./scripts/test.sh all

test-unit:
	./scripts/test.sh unit

test-integration:
	./scripts/test.sh integration

test-fast:
	./scripts/test.sh fast

test-coverage:
	./scripts/test.sh coverage

# Code Quality
lint:
	@echo "🔍 Running linting checks..."
	poetry run black --check src/ tests/
	poetry run isort --check-only src/ tests/
	poetry run ruff check src/ tests/

format:
	@echo "🎨 Formatting code..."
	poetry run black src/ tests/
	poetry run isort src/ tests/
	poetry run ruff check --fix src/ tests/

type-check:
	@echo "🔬 Running type checking..."
	poetry run mypy src/

# CI/CD
ci:
	./scripts/test.sh ci

clean:
	@echo "🧹 Cleaning up..."
	rm -rf .pytest_cache htmlcov .coverage dist/ build/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Development server
dev:
	@echo "🚀 Starting MCP server in development mode..."
	poetry run mcp-zephyr-scale-cloud

# Build package
build:
	@echo "📦 Building package..."
	poetry build

# Security check
security:
	@echo "🔒 Running security checks..."
	poetry run pip-audit
