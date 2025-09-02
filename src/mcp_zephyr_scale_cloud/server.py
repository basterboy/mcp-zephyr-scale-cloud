"""Enhanced MCP Server for Zephyr Scale Cloud with Pydantic schemas.

This file contains the Model Context Protocol (MCP) SERVER implementation
using Pydantic schemas for validation and type safety.
"""

import logging
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
from mcp.server import FastMCP

from .clients.zephyr_client import ZephyrClient
from .config import ZephyrConfig
from .utils.formatting import (
    format_error_message,
    format_folder_details,
    format_folder_list,
    format_priority_details,
    format_priority_list,
    format_status_details,
    format_status_list,
    format_success_message,
    format_validation_errors,
)
from .utils.validation import (
    validate_folder_data,
    validate_folder_type,
    validate_priority_data,
    validate_project_key,
    validate_status_data,
    validate_status_type,
)

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Error message constants
_CONFIG_ERROR_MSG = (
    "❌ ERROR: Zephyr Scale configuration not found. "
    "Please set ZEPHYR_SCALE_API_TOKEN environment variable."
)

# Global variables for configuration and client
config = None
zephyr_client = None


@asynccontextmanager
async def zephyr_server_lifespan(server):
    """
    Server lifespan context manager for startup and cleanup.

    This function is called when the MCP server starts and stops,
    allowing us to validate configuration and manage resources properly.
    """
    global config, zephyr_client

    # 🚀 STARTUP LOGIC
    logger.info("Zephyr Scale MCP Server starting up...")

    startup_errors = []

    try:
        # Load and validate configuration
        logger.info("Loading Zephyr Scale configuration...")
        config = ZephyrConfig.from_env()
        logger.info(
            "Configuration loaded successfully - Base URL: %s, Default Project: %s",
            config.base_url,
            config.project_key or "None",
        )

        # Initialize HTTP client
        logger.info("Initializing Zephyr Scale API client...")
        zephyr_client = ZephyrClient(config)
        logger.info("HTTP client initialized")

        # Test API connectivity
        logger.info("Testing API connectivity...")
        health_result = await zephyr_client.healthcheck()

        if health_result.is_valid and health_result.data.get("status") == "UP":
            logger.info("Zephyr Scale API connectivity verified")
        else:
            error_msg = (
                "; ".join(health_result.errors)
                if health_result.errors
                else "Unknown error"
            )
            startup_errors.append(f"API connectivity test failed: {error_msg}")
            logger.warning(
                "API connectivity test failed: %s - Server will start but API calls may fail",  # noqa: E501
                error_msg,
            )

    except ValueError as e:
        startup_errors.append(f"Configuration error: {str(e)}")
        logger.error(
            "Configuration error: %s - Server will start but tools will return configuration errors",  # noqa: E501
            str(e),
        )

    except Exception as e:
        startup_errors.append(f"Unexpected startup error: {str(e)}")
        logger.error("Unexpected startup error: %s", str(e))

    # Log startup result
    if not startup_errors:
        logger.info("Zephyr Scale MCP Server startup completed successfully!")
    else:
        logger.warning(
            "Zephyr Scale MCP Server started with %d warnings", len(startup_errors)
        )

    startup_result = {
        "config_valid": config is not None,
        "api_accessible": zephyr_client is not None and not startup_errors,
        "startup_errors": startup_errors,
        "tools_count": 12,  # We have 12 tools: healthcheck + 4 priorities + 4 statuses + 3 folders
        "base_url": config.base_url if config else None,
    }

    # Yield to allow server to run
    yield startup_result

    # 🧹 CLEANUP LOGIC
    logger.info("Zephyr Scale MCP Server shutting down...")

    # Clean up HTTP client resources
    if zephyr_client:
        logger.info("Cleaning up HTTP client resources...")
        # Note: httpx.AsyncClient is automatically cleaned up, but we could
        # add explicit cleanup here if we had persistent connections

    logger.info("Zephyr Scale MCP Server shutdown completed successfully!")


# Initialize MCP server with lifespan management
mcp = FastMCP("Zephyr Scale Cloud", lifespan=zephyr_server_lifespan)


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
async def get_priorities(
    project_key: Optional[str] = None, max_results: int = 50
) -> str:
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
    description: Optional[str] = None,
    color: Optional[str] = None,
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
    description: Optional[str] = None,
    color: Optional[str] = None,
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


# Status MCP Tools


@mcp.tool()
async def get_statuses(
    project_key: Optional[str] = None,
    status_type: Optional[str] = None,
    max_results: int = 50,
) -> str:
    """
    Get all statuses from Zephyr Scale Cloud.

    Args:
        project_key: Optional Jira project key to filter statuses (e.g., 'PROJ')
        status_type: Optional status type filter ('TEST_CASE', 'TEST_PLAN',
                 'TEST_CYCLE', 'TEST_EXECUTION')
        max_results: Maximum number of results to return (default: 50, max: 1000)

    Returns:
        str: Formatted list of statuses with their details
    """
    if not zephyr_client:
        return _CONFIG_ERROR_MSG

    # Validate status type if provided
    parsed_status_type = None
    if status_type:
        type_validation = validate_status_type(status_type)
        if not type_validation.is_valid:
            return format_validation_errors(type_validation.errors)

        # Import here to avoid circular imports
        from .schemas.status import StatusType

        parsed_status_type = StatusType(status_type)

    # Validate project key if provided
    if project_key:
        project_validation = validate_project_key(project_key)
        if not project_validation.is_valid:
            return format_validation_errors(project_validation.errors)

    result = await zephyr_client.get_statuses(
        project_key=project_key,
        status_type=parsed_status_type,
        max_results=max_results,
    )

    if result.is_valid:
        return format_status_list(result.data, project_key, status_type)
    else:
        return format_error_message(
            "Get Statuses", "Failed to retrieve statuses", "; ".join(result.errors)
        )


@mcp.tool()
async def get_status(status_id: int) -> str:
    """
    Get details of a specific status by its ID.

    Args:
        status_id: The ID of the status to retrieve

    Returns:
        str: Formatted status details
    """
    if not zephyr_client:
        return _CONFIG_ERROR_MSG

    if status_id < 1:
        return format_validation_errors(["Status ID must be a positive integer"])

    result = await zephyr_client.get_status(status_id)

    if result.is_valid:
        return format_status_details(result.data)
    else:
        return format_error_message(
            "Get Status",
            f"Failed to retrieve status {status_id}",
            "; ".join(result.errors),
        )


@mcp.tool()
async def create_status(
    project_key: str,
    name: str,
    status_type: str,
    description: Optional[str] = None,
    color: Optional[str] = None,
) -> str:
    """
    Create a new status in Zephyr Scale Cloud.

    Args:
        project_key: Jira project key where the status will be created (e.g., 'PROJ')
        name: Name of the status (max 255 characters)
        status_type: Status type ('TEST_CASE', 'TEST_PLAN', 'TEST_CYCLE',
                     'TEST_EXECUTION')
        description: Optional description of the status (max 255 characters)
        color: Optional color code for the status (e.g., '#FF0000')

    Returns:
        str: Result of the status creation
    """
    if not zephyr_client:
        return _CONFIG_ERROR_MSG

    # Validate input data using Pydantic schema
    request_data = {
        "projectKey": project_key,
        "name": name,
        "type": status_type,
        "description": description,
        "color": color,
    }

    validation_result = validate_status_data(request_data, is_update=False)
    if not validation_result.is_valid:
        return format_validation_errors(validation_result.errors)

    # Create status using validated schema
    result = await zephyr_client.create_status(validation_result.data)

    if result.is_valid:
        created_resource = result.data
        return format_success_message(
            "Created",
            "Status",
            created_resource.id,
            name=name,
            project_key=project_key,
            description=description,
            color=color,
            status_type=status_type,
            url=created_resource.self,
        )
    else:
        return format_error_message(
            "Create Status", "Failed to create status", "; ".join(result.errors)
        )


@mcp.tool()
async def update_status(
    status_id: int,
    project_id: int,
    name: str,
    index: int,
    archived: bool = False,
    default: bool = False,
    description: Optional[str] = None,
    color: Optional[str] = None,
) -> str:
    """
    Update an existing status in Zephyr Scale Cloud.

    Args:
        status_id: ID of the status to update
        project_id: ID of the project the status belongs to
        name: Updated name of the status (max 255 characters)
        index: Index/order position of the status (0-based)
        archived: Whether this status should be archived (default: False)
        default: Whether this should be the default status (default: False)
        description: Optional updated description (max 255 characters)
        color: Optional updated color code (e.g., '#FF0000')

    Returns:
        str: Result of the status update
    """
    if not zephyr_client:
        return _CONFIG_ERROR_MSG

    # Validate input data using Pydantic schema
    request_data = {
        "id": status_id,
        "project": {"id": project_id},
        "name": name,
        "index": index,
        "archived": archived,
        "default": default,
        "description": description,
        "color": color,
    }

    validation_result = validate_status_data(request_data, is_update=True)
    if not validation_result.is_valid:
        return format_validation_errors(validation_result.errors)

    # Update status using validated schema
    result = await zephyr_client.update_status(status_id, validation_result.data)

    if result.is_valid:
        return format_success_message(
            "Updated",
            "Status",
            status_id,
            name=name,
            index=index,
            archived=archived,
            default=default,
            description=description,
            color=color,
        )
    else:
        return format_error_message(
            "Update Status",
            f"Failed to update status {status_id}",
            "; ".join(result.errors),
        )


# Folder operations


@mcp.tool()
async def get_folders(
    project_key: Optional[str] = None,
    folder_type: Optional[str] = None,
    max_results: int = 50,
) -> str:
    """Get folders from Zephyr Scale Cloud.

    Args:
        project_key: Optional project key to filter folders
        folder_type: Optional folder type filter (TEST_CASE, TEST_PLAN, TEST_CYCLE)
        max_results: Maximum number of results to return (1-1000, default 50)

    Returns:
        Formatted list of folders or error message
    """
    if not zephyr_client:
        return format_error_message(
            "Get Folders", "Client not initialized", _CONFIG_ERROR_MSG
        )

    # Validate folder type if provided
    validated_folder_type = None
    if folder_type:
        folder_type_result = validate_folder_type(folder_type)
        if not folder_type_result:
            return format_error_message(
                "Get Folders",
                "Invalid folder type",
                folder_type_result.error_message,
            )
        validated_folder_type = folder_type_result.data

    # Validate project key if provided
    if project_key:
        project_key_result = validate_project_key(project_key)
        if not project_key_result:
            return format_error_message(
                "Get Folders",
                "Invalid project key",
                project_key_result.error_message,
            )

    # Get folders from API
    result = await zephyr_client.get_folders(
        project_key=project_key,
        folder_type=validated_folder_type,
        max_results=max_results,
    )

    if result:
        return format_folder_list(result.data, project_key, folder_type)
    else:
        return format_error_message(
            "Get Folders",
            "Failed to retrieve folders",
            "; ".join(result.errors),
        )


@mcp.tool()
async def get_folder(folder_id: int) -> str:
    """Get a specific folder by ID from Zephyr Scale Cloud.

    Args:
        folder_id: Folder ID to retrieve

    Returns:
        Formatted folder details or error message
    """
    if not zephyr_client:
        return format_error_message(
            "Get Folder", "Client not initialized", _CONFIG_ERROR_MSG
        )

    if folder_id < 1:
        return format_error_message(
            "Get Folder",
            "Invalid folder ID",
            "❌ Folder ID must be a positive integer",
        )

    # Get folder from API
    result = await zephyr_client.get_folder(folder_id)

    if result:
        return format_folder_details(result.data)
    else:
        return format_error_message(
            "Get Folder",
            f"Failed to retrieve folder {folder_id}",
            "; ".join(result.errors),
        )


@mcp.tool()
async def create_folder(
    name: str,
    project_key: str,
    folder_type: str,
    parent_id: Optional[int] = None,
) -> str:
    """Create a new folder in Zephyr Scale Cloud.

    Args:
        name: Folder name (1-255 characters)
        project_key: Jira project key
        folder_type: Folder type (TEST_CASE, TEST_PLAN, TEST_CYCLE)
        parent_id: Optional parent folder ID (null for root folders)

    Returns:
        Success message with created folder ID or error message
    """
    if not zephyr_client:
        return format_error_message(
            "Create Folder", "Client not initialized", _CONFIG_ERROR_MSG
        )

    # Build request data
    request_data = {
        "name": name,
        "projectKey": project_key,
        "folderType": folder_type,
    }

    if parent_id is not None:
        request_data["parentId"] = parent_id

    # Validate folder data
    validation_result = validate_folder_data(request_data)
    if not validation_result:
        return format_error_message(
            "Create Folder",
            "Invalid folder data",
            validation_result.error_message,
        )

    # Create folder via API
    result = await zephyr_client.create_folder(validation_result.data)

    if result:
        return format_success_message(
            "Created",
            "Folder",
            result.data.id,
            name=name,
            project_key=project_key,
            folder_type=folder_type,
            parent_id=parent_id,
        )
    else:
        return format_error_message(
            "Create Folder",
            f"Failed to create folder '{name}'",
            "; ".join(result.errors),
        )


def main():
    """Run the MCP server.

    This starts the MCP server that AI assistants can connect to.
    """
    mcp.run()


if __name__ == "__main__":
    main()
