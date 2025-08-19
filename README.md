# MCP Zephyr Scale Cloud Server

A Model Context Protocol (MCP) server for Zephyr Scale Cloud, enabling AI assistants to interact with test management capabilities.

## Features

- 🧪 Test case management
- 📊 Test execution and results
- 📈 Test reporting and analytics
- 🔄 Test cycle management
- 👥 Project and team management

## Installation

Using Poetry (recommended):
```bash
git clone https://github.com/basterboy/mcp-zephyr-scale-cloud.git
cd mcp-zephyr-scale-cloud
poetry install
```

Or using pip:
```bash
pip install mcp-zephyr-scale-cloud
```

## Configuration

Create a `.env` file with your Zephyr Scale Cloud credentials:

```bash
ZEPHYR_SCALE_API_TOKEN=your_api_token_here
ZEPHYR_SCALE_BASE_URL=https://api.zephyrscale.smartbear.com/v2
```

### Logging Configuration

The server uses Python's standard logging module. Configure logging levels as needed:

```python
import logging

# For development - see all startup details
logging.basicConfig(level=logging.INFO)

# For production - warnings and errors only  
logging.basicConfig(level=logging.WARNING)

# Custom format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Quick Start

1. **Set up environment variables:**
```bash
cp env.template .env
# Edit .env with your Zephyr Scale API token
```

2. **Install and run:**
```bash
poetry install
poetry run mcp-zephyr-scale-cloud
```

## Development

1. Clone the repository:
```bash
git clone https://github.com/basterboy/mcp-zephyr-scale-cloud.git
cd mcp-zephyr-scale-cloud
```

2. Install dependencies:
```bash
poetry install --with dev
```

3. Run tests:
```bash
# Run all tests
make test

# Or specific test types
make test-unit          # Unit tests only
make test-integration   # Integration tests only  
make test-fast         # Fast tests (no coverage)
make test-coverage     # Tests with detailed coverage

# Or use Poetry directly
poetry run pytest
```

4. Run code quality checks:
```bash
# Run all quality checks
make lint

# Or individual tools
poetry run black .      # Code formatting
poetry run isort .      # Import sorting
poetry run ruff check . # Linting
poetry run mypy src/    # Type checking
```

5. Auto-fix code issues:
```bash
make format  # Fix formatting and imports
```

## Architecture

This project implements an **MCP Server** that connects AI assistants to Zephyr Scale Cloud:

```
AI Assistant (Claude) 
    ↓ (MCP Protocol)
MCP Server (server.py) 
    ↓ (HTTP Requests)
Zephyr Scale Cloud API
```

### Project Structure

```
src/mcp_zephyr_scale_cloud/
├── server.py              # MCP Server - exposes tools to AI assistants
├── config.py              # Configuration management
├── schemas/               # Pydantic schemas for data validation
│   ├── __init__.py
│   ├── base.py           # Base schemas and common types
│   ├── common.py         # Shared entity schemas
│   ├── priority.py       # Priority-specific schemas
│   └── project.py        # Project-specific schemas
├── utils/                 # Utility functions
│   ├── __init__.py
│   ├── validation.py     # Input validation utilities
│   └── formatting.py     # Output formatting utilities
└── clients/
    ├── __init__.py
    └── zephyr_client.py   # Schema-based HTTP Client
```

### Key Concepts

- **MCP Server** (`server.py`): Handles the Model Context Protocol, exposes tools/resources to AI assistants with advanced lifespan management
- **HTTP Client** (`clients/zephyr_client.py`): Schema-based client making type-safe REST API calls to Zephyr Scale Cloud
- **Pydantic Schemas** (`schemas/`): Data validation and serialization using Pydantic models
- **Validation Utils** (`utils/validation.py`): Input validation with comprehensive error handling
- **Formatting Utils** (`utils/formatting.py`): Rich output formatting for MCP tools
- **Configuration** (`config.py`): Manages API tokens and settings
- **Server Lifespan**: Startup validation, API connectivity testing, and graceful shutdown management

## Advanced Features

### 🚀 Server Lifespan Management

This MCP server implements advanced [server lifespan management](https://github.com/modelcontextprotocol/python-sdk?tab=readme-ov-file#low-level-server) for robust production deployment:

- **Startup Validation**: Validates configuration and tests API connectivity before accepting requests
- **Fast Failure**: Reports configuration errors immediately on startup
- **Health Monitoring**: Automatically tests Zephyr Scale API accessibility during initialization 
- **Graceful Shutdown**: Properly cleans up resources when the server stops
- **Structured Logging**: Uses Python's logging module with proper log levels for production environments

**Benefits:**
- 🔧 **Better Developer Experience**: Clear error messages if API token is missing
- 🚨 **Production Ready**: Fails fast instead of silently accepting broken configurations
- 📊 **Monitoring**: Easy to detect configuration and connectivity issues
- 🧹 **Resource Management**: Proper cleanup prevents resource leaks

## Testing

This project includes comprehensive testing to ensure reliability:

### 🧪 Test Structure
```
tests/
├── test_basic.py           # Basic functionality tests
├── unit/                   # Unit tests for individual components
│   ├── test_config.py      # Configuration tests
│   ├── test_schemas.py     # Pydantic schema tests
│   ├── test_validation.py  # Validation utility tests
│   └── test_zephyr_client.py # HTTP client tests
├── integration/            # Integration tests
│   └── test_mcp_server.py  # MCP server integration tests
└── conftest.py            # Shared test fixtures
```

### 🚀 Running Tests
```bash
# Quick test run
make test-fast

# Full test suite with coverage
make test

# Continuous testing during development
poetry run pytest tests/ --tb=short -x

# Test specific functionality
poetry run pytest tests/test_basic.py -v
```

### 📊 Test Coverage
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test MCP server functionality end-to-end
- **Schema Tests**: Validate Pydantic models and API contracts
- **Validation Tests**: Ensure input validation works correctly

### 🔧 CI/CD
Tests run automatically on:
- **GitHub Actions**: On push/PR to main branch
- **Multiple Python versions**: 3.10, 3.11, 3.12
- **Code quality checks**: Formatting, linting, type checking

## MCP Tools

This server provides the following MCP tools:

### Currently Available:
- `healthcheck` - Check Zephyr Scale Cloud API connectivity and authentication status
- `get_priorities` - Get all priorities with optional project filtering
- `get_priority` - Get details of a specific priority by ID
- `create_priority` - Create a new priority in a project
- `update_priority` - Update an existing priority

### Planned:
- `get_projects` - List all available projects
- `get_test_cases` - Retrieve test cases from a project
- `create_test_case` - Create a new test case
- `update_test_case` - Update an existing test case
- `get_test_cycles` - Retrieve test cycles
- `create_test_execution` - Create test execution results
- `get_test_results` - Retrieve test execution results

## License

MIT License - see [LICENSE](LICENSE) file for details.
