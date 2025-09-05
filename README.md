# MCP Zephyr Scale Cloud Server

A Model Context Protocol (MCP) server for Zephyr Scale Cloud, enabling AI assistants to interact with test management capabilities.

## Features

### ✅ **Currently Implemented:**
- 🩺 **API Health Monitoring** - Check connectivity and authentication status
- ⭐ **Priority Management** - Create, read, update priorities across projects
- 📊 **Status Management** - Manage test execution statuses with type filtering
- 📁 **Folder Management** - Organize test artifacts with hierarchical folder structure
- 🧪 **Test Case Management** - Full CRUD operations for test cases with metadata
- 📝 **Test Steps & Scripts** - Manage test step definitions and scripts (plain/BDD)
- 🔗 **Test Case Links** - Link test cases to Jira issues and web resources
- 📋 **Test Case Retrieval** - Advanced pagination and filtering capabilities
- 📚 **Version Management** - Test case version history and retrieval
- 🔧 **Production Ready** - Server lifespan management and structured logging
- 🧪 **Comprehensive Testing** - Unit tests, integration tests, and CI/CD pipeline
- 📝 **Type Safety** - Pydantic schema validation for all API operations

### 🚧 **Planned Features:**

Based on the Zephyr Scale Cloud API documentation, the following major categories are planned for implementation:

- 🔄 **Test Cycle Management** - Create, read, update test cycles with metadata
- 📈 **Test Execution Management** - Create, read, update test executions and results
- 📋 **Test Plan Management** - Test plan operations and organization  
- 🌍 **Environment Management** - Test environment configuration and management
- 👥 **Project Management** - Project information and configuration
- 🔗 **Advanced Link Management** - Delete links and enhanced link operations
- 🤖 **Automation Integration** - Custom, Cucumber, and JUnit test execution automation
- 📊 **Issue Link Coverage** - Comprehensive Jira issue link coverage tracking

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

# Optional: Default project key for tools that support it
ZEPHYR_SCALE_DEFAULT_PROJECT_KEY=MYPROJ
```

### Environment Variable Fallback

Many tools now support automatic project key resolution. If you have access to multiple projects, you can set `ZEPHYR_SCALE_DEFAULT_PROJECT_KEY` to avoid specifying the project key in every tool call. Tools like `get_test_cases`, `get_folders`, and others will automatically use this default when no explicit project key is provided.

## Installation

### Option 1: Install from GitHub Releases (Recommended)

Download and install the latest release directly from GitHub:

```bash
# Download the latest wheel file from GitHub releases
pip install https://github.com/basterboy/mcp-zephyr-scale-cloud/releases/download/v0.1.3/mcp_zephyr_scale_cloud-0.1.3-py3-none-any.whl
```

Or install from the source distribution:

```bash
pip install https://github.com/basterboy/mcp-zephyr-scale-cloud/releases/download/v0.1.3/mcp_zephyr_scale_cloud-0.1.3.tar.gz
```

### Option 2: Install from PyPI (Recommended)

Install directly from the Python Package Index:

```bash
pip install mcp-zephyr-scale-cloud
```

### Option 3: Install from Source

For development or latest features:

```bash
git clone https://github.com/basterboy/mcp-zephyr-scale-cloud.git
cd mcp-zephyr-scale-cloud
pip install .
```

### Verify Installation

After installation, verify it works:

```bash
python -c "import mcp_zephyr_scale_cloud; print('✅ Successfully installed!')"
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

## Recent Improvements

### 🚀 **Major Updates:**
- **Test Case Management**: Full CRUD operations for test cases with advanced metadata support
- **Performance Optimization**: Added comprehensive pagination guidance with max_results=1000 recommendations  
- **Link Management**: Test case linking to Jira issues and web resources
- **Version Control**: Test case version history and retrieval capabilities
- **Environment Integration**: Automatic project key resolution from environment variables
- **Enhanced Error Handling**: Improved validation and user-friendly error messages

### 🔧 **Technical Improvements:**
- **Schema Simplification**: Streamlined update operations using Pydantic model_dump()
- **Validation Enhancement**: Comprehensive input validation with helpful error guidance
- **Code Quality**: Extensive refactoring for maintainability and performance
- **Test Coverage**: Expanded test suite covering all new functionality

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
│   ├── folder.py         # Folder-specific schemas
│   ├── test_case.py      # Test case schemas with pagination support
│   ├── test_script.py    # Test script schemas
│   ├── test_step.py      # Test step schemas
│   └── version.py        # Version-specific schemas
├── utils/                 # Utility functions
│   ├── __init__.py
│   └── validation.py     # Input validation utilities
└── clients/
    ├── __init__.py
    └── zephyr_client.py   # Schema-based HTTP Client
```

### Key Concepts

- **MCP Server** (`server.py`): Handles the Model Context Protocol, exposes tools/resources to AI assistants with advanced lifespan management
- **HTTP Client** (`clients/zephyr_client.py`): Schema-based client making type-safe REST API calls to Zephyr Scale Cloud
- **Pydantic Schemas** (`schemas/`): Data validation and serialization using Pydantic models
- **Validation Utils** (`utils/validation.py`): Input validation with comprehensive error handling
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

This server provides **25 MCP tools** for Zephyr Scale Cloud integration:

| **Category** | **Tools** | **Description** |
|--------------|-----------|-----------------|
| **Health** | 1 tool | API connectivity and authentication |
| **Priorities** | 4 tools | Full CRUD operations for priority management |
| **Statuses** | 4 tools | Full CRUD operations for status management |
| **Folders** | 3 tools | Folder management and organization |
| **Test Steps** | 2 tools | Test step retrieval and creation |
| **Test Scripts** | 2 tools | Test script retrieval and creation |
| **Test Cases** | 7 tools | Complete test case management suite |
| **Test Case Links** | 2 tools | Link management for test cases |
| **Total** | **25 tools** | **Production-ready MCP server** |

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

#### **📁 Folder Management**
- `get_folders` - Get all folders with optional project and type filtering
- `get_folder` - Get details of a specific folder by ID
- `create_folder` - Create a new folder in a project

#### **📝 Test Step Management**
- `get_test_steps` - Retrieve test steps for a specific test case with pagination support
- `create_test_steps` - Create test steps for a test case with APPEND/OVERWRITE modes

#### **📄 Test Script Management**
- `get_test_script` - Retrieve test script for a specific test case
- `create_test_script` - Create or update test script with plain text or BDD format

#### **📋 Test Case Management**
- `get_test_case` - Get detailed test case information including metadata, status, priority, and content
- `get_test_cases` - Retrieve test cases with advanced offset-based pagination and filtering
- `create_test_case` - Create new test cases with comprehensive metadata support
- `update_test_case` - Update existing test cases with validation and error handling
- `get_test_case_versions` - Retrieve version history for test cases
- `get_test_case_version` - Get specific version of a test case
- `get_links` - Get all links (issues + web links) associated with a test case

#### **🔗 Test Case Links**
- `create_issue_link` - Link test cases to Jira issues for traceability
- `create_web_link` - Add web links to test cases for documentation

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

## 📁 Folder Operations Guide

Folder operations allow you to organize and manage test artifacts in Zephyr Scale Cloud. Folders provide hierarchical structure for test cases, test plans, and test cycles.

### **Folder Types:**
- `TEST_CASE` - For organizing test cases
- `TEST_PLAN` - For organizing test plans  
- `TEST_CYCLE` - For organizing test cycles

### **Example Usage:**

```python
# Get all folders for a specific project and type
folders = await get_folders(
    project_key="MYPROJ",
    folder_type="TEST_CASE",
    max_results=100
)

# Create a new root folder
root_folder = await create_folder(
    name="Smoke Tests",
    project_key="MYPROJ",
    folder_type="TEST_CASE"
    # parent_id is None for root folders
)

# Create a child folder
child_folder = await create_folder(
    name="Login Tests",
    project_key="MYPROJ", 
    folder_type="TEST_CASE",
    parent_id=123  # ID of the parent folder
)

# Get details of a specific folder
folder_details = await get_folder(folder_id=456)
```

### **Folder Properties:**
- **Name**: Human-readable folder name (1-255 chars)
- **Type**: One of the three folder types listed above
- **Project Key**: Jira project key where the folder belongs
- **Parent ID**: ID of parent folder (null for root folders)
- **Index**: Position/order within the parent folder
- **ID**: Unique identifier assigned by Zephyr Scale

### **Folder Hierarchy:**
- Folders can be nested to create hierarchical organization
- Root folders have `parent_id = null`
- Child folders reference their parent via `parent_id`
- Each folder type maintains its own hierarchy within a project

## 🔧 Test Case Management Guide

The test case management tools provide comprehensive CRUD operations for managing test cases in Zephyr Scale Cloud.

### **Key Features:**
- **Full CRUD Operations**: Create, read, update, and retrieve test cases
- **Advanced Pagination**: Efficient offset-based pagination with performance optimizations
- **Version Management**: Access to test case version history
- **Link Management**: Connect test cases to Jira issues and web resources
- **Rich Metadata**: Support for priorities, statuses, folders, components, and custom fields
- **Environment Integration**: Automatic project key resolution from environment variables

### **Pagination Performance Tips:**
- Use `max_results=1000` for fastest bulk data retrieval
- Follow offset-based pagination: `start_at = current_start_at + max_results`
- Ensure `start_at` is a multiple of `max_results` (API requirement)
- Check `len(values) < max_results` to detect the last page

### **Example Usage:**

```python
# Get test cases with maximum performance
test_cases = await get_test_cases(
    project_key="MYPROJ",
    max_results=1000,  # Maximum for best performance
    start_at=0
)

# Create a comprehensive test case
new_test_case = await create_test_case(
    name="Login functionality test",
    project_key="MYPROJ",
    objective="Verify user can log in successfully",
    priority_name="High",
    status_name="Draft",
    folder_id=123,
    labels=["smoke", "authentication"]
)

# Update test case with validation
updated = await update_test_case(
    test_case_key="MYPROJ-T123",
    name="Updated login test",
    priority_id=456,
    status_id=789
)

# Link to Jira issue for traceability
link_result = await create_issue_link(
    test_case_key="MYPROJ-T123",
    issue_id=456789
)
```

## License

MIT License - see [LICENSE](LICENSE) file for details.
