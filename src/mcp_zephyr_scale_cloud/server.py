"""Enhanced MCP Server for Zephyr Scale Cloud with Pydantic schemas.

This file contains the Model Context Protocol (MCP) SERVER implementation
using Pydantic schemas for validation and type safety.
"""

from dotenv import load_dotenv
from mcp.server import FastMCP

from .clients.zephyr_client import ZephyrClient
from .config import ZephyrConfig
from .utils.formatting import (
    format_error_message,
    format_priority_details,
    format_priority_list,
    format_success_message,
    format_validation_errors,
)
from .utils.validation import (
    validate_priority_data,
    validate_project_key,
)

# Load environment variables
load_dotenv()

# Initialize MCP server
mcp = FastMCP("Zephyr Scale Cloud")

# Error message constants
_CONFIG_ERROR_MSG = (
    "❌ ERROR: Zephyr Scale configuration not found. "
    "Please set ZEPHYR_SCALE_API_TOKEN environment variable."
)

# Initialize HTTP client for Zephyr Scale API
try:
    config = ZephyrConfig.from_env()
    zephyr_client = ZephyrClient(config)
except ValueError:
    # If config fails, we'll create a dummy client for error reporting
    config = None
    zephyr_client = None


@mcp.tool()
async def healthcheck() -> str:
    """
    Check the health status of the Zephyr Scale Cloud API connection.

    This is an MCP TOOL that AI assistants can call.
    Internally, it uses the HTTP client to make requests to Zephyr Scale.

    Returns:
        str: Health status information including API connectivity and
            authentication status.
    """
    if not zephyr_client:
        return _CONFIG_ERROR_MSG

    result = await zephyr_client.healthcheck()

    if result.is_valid and result.data.get("status") == "UP":
        return (
            f"✅ SUCCESS: Zephyr Scale Cloud API is healthy\n"
            f"📍 Base URL: {config.base_url}\n"
            f"🔑 Authentication: Valid\n"
            f"📊 Status: {result.data.get('status', 'Unknown')}"
        )
    else:
        return format_error_message(
            "Health Check",
            "Zephyr Scale Cloud API health check failed",
            "; ".join(result.errors) if result.errors else "Unknown error",
        )


@mcp.tool()
async def get_priorities(project_key: str | None = None, max_results: int = 50) -> str:
    """
    Get all priorities from Zephyr Scale Cloud.

    Args:
        project_key: Optional Jira project key to filter priorities (e.g., 'PROJ')
        max_results: Maximum number of results to return (default: 50, max: 1000)

    Returns:
        str: Formatted list of priorities with their details
    """
    if not zephyr_client:
        return _CONFIG_ERROR_MSG

    # Validate project key if provided
    if project_key:
        project_validation = validate_project_key(project_key)
        if not project_validation:
            return format_validation_errors(project_validation.errors)

    result = await zephyr_client.get_priorities(
        project_key=project_key, max_results=max_results
    )

    if result.is_valid:
        return format_priority_list(result.data, project_key)
    else:
        return format_error_message(
            "Get Priorities", "Failed to retrieve priorities", "; ".join(result.errors)
        )


@mcp.tool()
async def get_priority(priority_id: int) -> str:
    """
    Get details of a specific priority by its ID.

    Args:
        priority_id: The ID of the priority to retrieve

    Returns:
        str: Formatted priority details
    """
    if not zephyr_client:
        return _CONFIG_ERROR_MSG

    result = await zephyr_client.get_priority(priority_id)

    if result.is_valid:
        return format_priority_details(result.data)
    else:
        return format_error_message(
            "Get Priority",
            f"Failed to retrieve priority {priority_id}",
            "; ".join(result.errors),
        )


@mcp.tool()
async def create_priority(
    project_key: str,
    name: str,
    description: str | None = None,
    color: str | None = None,
) -> str:
    """
    Create a new priority in Zephyr Scale Cloud.

    Args:
        project_key: Jira project key where the priority will be created (e.g., 'PROJ')
        name: Name of the priority (max 255 characters)
        description: Optional description of the priority (max 255 characters)
        color: Optional color code for the priority (e.g., '#FF0000')

    Returns:
        str: Result of the priority creation
    """
    if not zephyr_client:
        return _CONFIG_ERROR_MSG

    # Validate input data using Pydantic schema
    request_data = {
        "projectKey": project_key,
        "name": name,
        "description": description,
        "color": color,
    }

    validation_result = validate_priority_data(request_data, is_update=False)
    if not validation_result:
        return format_validation_errors(validation_result.errors)

    # Create priority using validated schema
    result = await zephyr_client.create_priority(validation_result.data)

    if result.is_valid:
        created_resource = result.data
        return format_success_message(
            "Created",
            "Priority",
            created_resource.id,
            name=name,
            project_key=project_key,
            description=description,
            color=color,
            url=created_resource.self,
        )
    else:
        return format_error_message(
            "Create Priority", "Failed to create priority", "; ".join(result.errors)
        )


@mcp.tool()
async def update_priority(
    priority_id: int,
    project_id: int,
    name: str,
    index: int,
    default: bool = False,
    description: str | None = None,
    color: str | None = None,
) -> str:
    """
    Update an existing priority in Zephyr Scale Cloud.

    Args:
        priority_id: ID of the priority to update
        project_id: ID of the project the priority belongs to
        name: Updated name of the priority (max 255 characters)
        index: Index/order position of the priority (0-based)
        default: Whether this should be the default priority (default: False)
        description: Optional updated description (max 255 characters)
        color: Optional updated color code (e.g., '#FF0000')

    Returns:
        str: Result of the priority update
    """
    if not zephyr_client:
        return _CONFIG_ERROR_MSG

    # Validate input data using Pydantic schema
    request_data = {
        "id": priority_id,
        "project": {"id": project_id},
        "name": name,
        "description": description,
        "index": index,
        "default": default,
        "color": color,
    }

    validation_result = validate_priority_data(request_data, is_update=True)
    if not validation_result:
        return format_validation_errors(validation_result.errors)

    # Update priority using validated schema
    result = await zephyr_client.update_priority(priority_id, validation_result.data)

    if result.is_valid:
        return format_success_message(
            "Updated",
            "Priority",
            priority_id,
            name=name,
            project_id=project_id,
            index=index,
            default=default,
            description=description,
            color=color,
        )
    else:
        return format_error_message(
            "Update Priority",
            f"Failed to update priority {priority_id}",
            "; ".join(result.errors),
        )


def main():
    """Run the MCP server.

    This starts the MCP server that AI assistants can connect to.
    """
    mcp.run()


if __name__ == "__main__":
    main()
