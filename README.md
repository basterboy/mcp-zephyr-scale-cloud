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
poetry run pytest
```

4. Run linting:
```bash
poetry run black .
poetry run isort .
poetry run ruff check .
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
└── clients/
    ├── __init__.py
    └── zephyr_client.py    # HTTP Client - makes REST API calls
```

### Key Concepts

- **MCP Server** (`server.py`): Handles the Model Context Protocol, exposes tools/resources to AI assistants
- **HTTP Client** (`clients/zephyr_client.py`): Makes REST API calls to Zephyr Scale Cloud
- **Configuration** (`config.py`): Manages API tokens and settings

## MCP Tools

This server provides the following MCP tools:

### Currently Available:
- `healthcheck` - Check Zephyr Scale Cloud API connectivity and authentication status

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
