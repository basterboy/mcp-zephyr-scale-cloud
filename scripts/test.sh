#!/bin/bash
# Test runner script for MCP Zephyr Scale Cloud

set -e  # Exit on any error

echo "🧪 Running MCP Zephyr Scale Cloud Test Suite"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    print_error "Must be run from project root directory"
    exit 1
fi

# Install dependencies if needed
print_status "Checking dependencies..."
if ! poetry run python -c "import pytest" 2>/dev/null; then
    print_status "Installing test dependencies..."
    poetry install --with dev
fi

# Set test environment variables
export ZEPHYR_SCALE_API_TOKEN="test_token_for_testing"
export ZEPHYR_SCALE_BASE_URL="https://api.example.com/v2"
export ZEPHYR_SCALE_DEFAULT_PROJECT_KEY="TEST"

# Clean up any previous test artifacts
print_status "Cleaning up previous test artifacts..."
rm -rf .pytest_cache htmlcov .coverage

# Run linting first
print_status "Running code quality checks..."
poetry run black --check src/ tests/ || {
    print_warning "Code formatting issues found. Run 'poetry run black src/ tests/' to fix."
}

poetry run isort --check-only src/ tests/ || {
    print_warning "Import sorting issues found. Run 'poetry run isort src/ tests/' to fix."
}

poetry run ruff check src/ tests/ || {
    print_warning "Linting issues found. Run 'poetry run ruff check --fix src/ tests/' to fix."
}

# Run type checking
print_status "Running type checking..."
poetry run mypy src/ || {
    print_warning "Type checking issues found."
}

# Run tests based on arguments
case "${1:-all}" in
    "unit")
        print_status "Running unit tests only..."
        poetry run pytest tests/unit/ -v
        ;;
    "integration") 
        print_status "Running integration tests only..."
        poetry run pytest tests/integration/ -v
        ;;
    "fast")
        print_status "Running fast tests only (no coverage)..."
        poetry run pytest tests/ -v --no-cov -x
        ;;
    "coverage")
        print_status "Running tests with detailed coverage..."
        poetry run pytest tests/ -v --cov-report=html --cov-report=term-missing
        print_status "Coverage report generated in htmlcov/"
        ;;
    "ci")
        print_status "Running CI test suite..."
        poetry run pytest tests/ -v --tb=short --strict-markers
        ;;
    "all"|*)
        print_status "Running complete test suite..."
        poetry run pytest tests/ -v
        ;;
esac

test_exit_code=$?

if [ $test_exit_code -eq 0 ]; then
    print_success "All tests passed! ✅"
    
    # Show coverage summary if available
    if [ -f ".coverage" ]; then
        echo ""
        print_status "Coverage Summary:"
        poetry run coverage report --show-missing --skip-covered
    fi
    
    echo ""
    print_success "Test suite completed successfully!"
    echo "🚀 Ready for deployment!"
else
    print_error "Some tests failed! ❌"
    echo ""
    print_error "Please fix the failing tests before continuing."
    exit $test_exit_code
fi
