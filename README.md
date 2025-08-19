# MCP Zephyr Scale Cloud Server

A Model Context Protocol (MCP) server for Zephyr Scale Cloud, enabling AI assistants to interact with test management capabilities.

## Features

### ✅ **Currently Implemented:**
- 🩺 **API Health Monitoring** - Check connectivity and authentication status
- ⭐ **Priority Management** - Create, read, update priorities across projects
- 📊 **Status Management** - Manage test execution statuses with type filtering
- 🔧 **Production Ready** - Server lifespan management and structured logging
- 🧪 **Comprehensive Testing** - Unit tests, integration tests, and CI/CD pipeline
- 📝 **Type Safety** - Pydantic schema validation for all API operations

### 🚧 **Planned Features:**
- 🧪 Test case management
- 📈 Test execution and results
- 🔄 Test cycle management
- 👥 Project and team management
- 📊 Test reporting and analytics

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

3. **Test your connection:**
```bash
# Check if your setup works
poetry run python -c "
from src.mcp_zephyr_scale_cloud.config import ZephyrConfig
from src.mcp_zephyr_scale_cloud.clients.zephyr_client import ZephyrClient
import asyncio

async def test():
    config = ZephyrConfig.from_env()
    client = ZephyrClient(config)
    result = await client.healthcheck()
    print(f'API Status: {result.data.get(\"status\") if result.is_valid else \"Failed\"}')

asyncio.run(test())
"
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
│   ├── status.py         # Status-specific schemas
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

This server provides **9 MCP tools** for Zephyr Scale Cloud integration:

| **Category** | **Tools** | **Description** |
|--------------|-----------|-----------------|
| **Health** | 1 tool | API connectivity and authentication |
| **Priorities** | 4 tools | Full CRUD operations for priority management |
| **Statuses** | 4 tools | Full CRUD operations for status management |
| **Total** | **9 tools** | **Production-ready MCP server** |

### Currently Available:

#### **🩺 Health & Connectivity**
- `healthcheck` - Check Zephyr Scale Cloud API connectivity and authentication status

#### **⭐ Priority Management**
- `get_priorities` - Get all priorities with optional project filtering
- `get_priority` - Get details of a specific priority by ID
- `create_priority` - Create a new priority in a project
- `update_priority` - Update an existing priority

#### **📊 Status Management**
- `get_statuses` - Get all statuses with optional project and type filtering
- `get_status` - Get details of a specific status by ID
- `create_status` - Create a new status in a project
- `update_status` - Update an existing status

## 📊 Status Operations Guide

Status operations allow you to manage test execution statuses in Zephyr Scale Cloud. Each status can be associated with different entity types:

### **Status Types:**
- `TEST_CASE` - For test case statuses
- `TEST_PLAN` - For test plan statuses  
- `TEST_CYCLE` - For test cycle statuses
- `TEST_EXECUTION` - For test execution statuses

### **Example Usage:**

```python
# Get all statuses for a specific project and type
statuses = await get_statuses(
    project_key="MYPROJ",
    status_type="TEST_EXECUTION",
    max_results=100
)

# Create a new test execution status
new_status = await create_status(
    project_key="MYPROJ",
    name="In Review",
    status_type="TEST_EXECUTION",
    description="Test is under review",
    color="#FFA500"
)

# Update an existing status
updated = await update_status(
    status_id=123,
    project_id=456,
    name="Reviewed",
    index=5,
    description="Test has been reviewed and approved"
)
```

### **Status Properties:**
- **Name**: Human-readable status name (max 255 chars)
- **Type**: One of the four status types listed above
- **Description**: Optional detailed description (max 255 chars)
- **Color**: Optional hex color code (e.g., '#FF0000')
- **Index**: Position/order in status lists
- **Default**: Whether this is the default status for the type
- **Archived**: Whether the status is archived

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
