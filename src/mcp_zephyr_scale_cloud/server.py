"""Enhanced MCP Server for Zephyr Scale Cloud with Pydantic schemas.

This file contains the Model Context Protocol (MCP) SERVER implementation
using Pydantic schemas for validation and type safety.
"""

import logging
from contextlib import asynccontextmanager

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
    format_test_case_creation_success,
    format_test_case_display,
    format_test_case_links_display,
    format_test_case_versions_list,
    format_test_script_display,
    format_test_steps_list,
    format_validation_errors,
)
from .utils.validation import (
    validate_component_id,
    validate_estimated_time,
    validate_folder_data,
    validate_folder_id,
    validate_folder_type,
    validate_issue_id,
    validate_issue_link_input,
    validate_priority_data,
    validate_project_key,
    validate_status_data,
    validate_status_type,
    validate_test_case_input,
    validate_test_case_key,
    validate_test_case_name,
    validate_test_script_input,
    validate_test_script_type,
    validate_test_steps_input,
    validate_test_steps_mode,
    validate_version_number,
    validate_web_link_input,
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
        "tools_count": 23,
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


# Status MCP Tools


@mcp.tool()
async def get_statuses(
    project_key: str | None = None,
    status_type: str | None = None,
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
    description: str | None = None,
    color: str | None = None,
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
    description: str | None = None,
    color: str | None = None,
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
    project_key: str | None = None,
    folder_type: str | None = None,
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

    if result.is_valid:
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

    if result.is_valid:
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
    parent_id: str | None = None,
) -> str:
    """Create a new folder in Zephyr Scale Cloud.

    Args:
        name: Folder name (1-255 characters)
        project_key: Jira project key
        folder_type: Folder type (TEST_CASE, TEST_PLAN, TEST_CYCLE)
        parent_id: Optional parent folder ID as string (null for root folders)

    Returns:
        Success message with created folder ID or error message
    """
    # Convert and validate parent_id if provided
    parsed_parent_id = None
    if parent_id is not None:
        try:
            parsed_parent_id = int(parent_id)
            if parsed_parent_id <= 0:
                return format_error_message(
                    "Create Folder",
                    "Invalid parent folder ID",
                    "Parent folder ID must be a positive integer",
                )
        except (ValueError, TypeError):
            return format_error_message(
                "Create Folder",
                "Invalid parent folder ID",
                f"Parent folder ID must be a valid integer, got: {parent_id}",
            )

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

    if parsed_parent_id is not None:
        request_data["parentId"] = parsed_parent_id

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

    if result.is_valid:
        return format_success_message(
            "Created",
            "Folder",
            result.data.id,
            name=name,
            project_key=project_key,
            folder_type=folder_type,
            parent_id=parsed_parent_id,
        )
    else:
        return format_error_message(
            "Create Folder",
            f"Failed to create folder '{name}'",
            "; ".join(result.errors),
        )


@mcp.tool()
async def get_test_steps(
    test_case_key: str,
    max_results: int = 10,
    start_at: int = 0,
) -> str:
    """Get test steps for a specific test case from Zephyr Scale Cloud.

    Args:
        test_case_key: The key of the test case (format: [PROJECT]-T[NUMBER])
        max_results: Maximum number of results to return (default: 10, max: 1000)
        start_at: Zero-indexed starting position (default: 0)

    Returns:
        Formatted list of test steps or error message
    """
    if not zephyr_client:
        return format_error_message(
            "Get Test Steps", "Client not initialized", _CONFIG_ERROR_MSG
        )

    # Validate test case key
    test_case_validation = validate_test_case_key(test_case_key)
    if not test_case_validation.is_valid:
        return format_error_message(
            "Get Test Steps",
            "Invalid test case key",
            "; ".join(test_case_validation.errors),
        )

    # Get test steps from API
    result = await zephyr_client.get_test_steps(
        test_case_key=test_case_key,
        max_results=max_results,
        start_at=start_at,
    )

    if result.is_valid:
        return format_test_steps_list(result.data, test_case_key, max_results, start_at)
    else:
        return format_error_message(
            "Get Test Steps",
            f"Failed to retrieve test steps for {test_case_key}",
            "; ".join(result.errors),
        )


@mcp.tool()
async def create_test_steps(
    test_case_key: str,
    mode: str,
    steps: str,
) -> str:
    """Create test steps for a specific test case in Zephyr Scale Cloud.

    Args:
        test_case_key: The key of the test case (format: [PROJECT]-T[NUMBER])
        mode: Operation mode - "APPEND" adds to existing, "OVERWRITE" replaces all
        steps: JSON string with test step objects. Each step should have either:
               - "inline": {"description": "...", "testData": "...",
                          "expectedResult": "..."}
               - "testCase": {"testCaseKey": "...", "parameters": [...]}

    Returns:
        Success message with created test steps or error message
    """
    if not zephyr_client:
        return format_error_message(
            "Create Test Steps", "Client not initialized", _CONFIG_ERROR_MSG
        )

    # Validate test case key
    test_case_validation = validate_test_case_key(test_case_key)
    if not test_case_validation.is_valid:
        return format_error_message(
            "Create Test Steps",
            "Invalid test case key",
            "; ".join(test_case_validation.errors),
        )

    # Validate mode
    mode_validation = validate_test_steps_mode(mode)
    if not mode_validation.is_valid:
        return format_error_message(
            "Create Test Steps",
            "Invalid mode",
            "; ".join(mode_validation.errors),
        )

    # Parse and validate steps JSON
    try:
        import json

        steps_data = json.loads(steps)
        if not isinstance(steps_data, list):
            return format_error_message(
                "Create Test Steps",
                "Invalid steps format",
                "Steps must be a JSON array",
            )
    except json.JSONDecodeError as e:
        return format_error_message(
            "Create Test Steps",
            "Invalid JSON format",
            f"Failed to parse steps JSON: {str(e)}",
        )

    # Build and validate test steps input
    test_steps_input_data = {
        "mode": mode_validation.data,
        "items": steps_data,
    }

    validation_result = validate_test_steps_input(test_steps_input_data)
    if not validation_result.is_valid:
        return format_error_message(
            "Create Test Steps",
            "Invalid test steps data",
            "; ".join(validation_result.errors),
        )

    # Create test steps via API
    result = await zephyr_client.create_test_steps(
        test_case_key=test_case_key,
        test_steps_input=validation_result.data,
    )

    if result.is_valid:
        return format_success_message(
            "Created",
            "Test Steps",
            "Successfully created test steps",
            test_case_key=test_case_key,
            mode=mode,
            resource_id=result.data.id,
        )
    else:
        return format_error_message(
            "Create Test Steps",
            f"Failed to create test steps for {test_case_key}",
            "; ".join(result.errors),
        )


@mcp.tool()
async def get_test_script(test_case_key: str) -> str:
    """Get test script for a specific test case in Zephyr Scale Cloud.

    Args:
        test_case_key: The key of the test case (format: [PROJECT]-T[NUMBER])

    Returns:
        Formatted test script information or error message
    """
    if not zephyr_client:
        return format_error_message(
            "Get Test Script", "Client not initialized", _CONFIG_ERROR_MSG
        )

    # Validate test case key
    test_case_validation = validate_test_case_key(test_case_key)
    if not test_case_validation.is_valid:
        return format_error_message(
            "Get Test Script",
            "Invalid test case key",
            "; ".join(test_case_validation.errors),
        )

    # Get test script via API
    result = await zephyr_client.get_test_script(test_case_key=test_case_key)

    if result.is_valid:
        return format_test_script_display(result.data)
    else:
        return format_error_message(
            "Get Test Script",
            f"Failed to retrieve test script for {test_case_key}",
            "; ".join(result.errors),
        )


@mcp.tool()
async def create_test_script(
    test_case_key: str,
    script_type: str,
    text: str,
) -> str:
    """Create or update test script for a specific test case in Zephyr Scale Cloud.

    Args:
        test_case_key: The key of the test case (format: [PROJECT]-T[NUMBER])
        script_type: Script type - "plain" for plain text or "bdd" for BDD format
        text: The test script content (minimum 1 character)

    Returns:
        Success message with created test script or error message
    """
    if not zephyr_client:
        return format_error_message(
            "Create Test Script", "Client not initialized", _CONFIG_ERROR_MSG
        )

    # Validate test case key
    test_case_validation = validate_test_case_key(test_case_key)
    if not test_case_validation.is_valid:
        return format_error_message(
            "Create Test Script",
            "Invalid test case key",
            "; ".join(test_case_validation.errors),
        )

    # Validate script type
    type_validation = validate_test_script_type(script_type)
    if not type_validation.is_valid:
        return format_error_message(
            "Create Test Script",
            "Invalid script type",
            "; ".join(type_validation.errors),
        )

    # Build and validate test script input
    test_script_input_data = {
        "type": type_validation.data,
        "text": text,
    }

    validation_result = validate_test_script_input(test_script_input_data)
    if not validation_result.is_valid:
        return format_error_message(
            "Create Test Script",
            "Invalid test script data",
            "; ".join(validation_result.errors),
        )

    # Create test script via API
    result = await zephyr_client.create_test_script(
        test_case_key=test_case_key,
        test_script_input=validation_result.data,
    )

    if result.is_valid:
        return format_success_message(
            "Created",
            "Test Script",
            "Successfully created test script",
            test_case_key=test_case_key,
            script_type=script_type,
            resource_id=result.data.id,
        )
    else:
        return format_error_message(
            "Create Test Script",
            f"Failed to create test script for {test_case_key}",
            "; ".join(result.errors),
        )


@mcp.tool()
async def get_test_case(test_case_key: str) -> str:
    """Get detailed information for a specific test case in Zephyr Scale Cloud.

    Args:
        test_case_key: The key of the test case (format: [PROJECT]-T[NUMBER])

    Returns:
        Formatted test case information or error message
    """
    if not zephyr_client:
        return format_error_message(
            "Get Test Case", "Client not initialized", _CONFIG_ERROR_MSG
        )

    # Validate test case key
    test_case_validation = validate_test_case_key(test_case_key)
    if not test_case_validation.is_valid:
        return format_error_message(
            "Get Test Case",
            "Invalid test case key",
            "; ".join(test_case_validation.errors),
        )

    # Get test case via API
    result = await zephyr_client.get_test_case(test_case_key=test_case_key)

    if result.is_valid:
        return format_test_case_display(result.data)
    else:
        return format_error_message(
            "Get Test Case",
            f"Failed to retrieve test case {test_case_key}",
            "; ".join(result.errors),
        )


@mcp.tool()
async def get_test_case_versions(
    test_case_key: str, max_results: int = 10, start_at: int = 0
) -> str:
    """Get all versions for a test case in Zephyr Scale Cloud.

    Args:
        test_case_key: The key of the test case (format: [PROJECT]-T[NUMBER])
        max_results: Maximum number of results to return (default: 10, max: 1000)
        start_at: Zero-indexed starting position (default: 0)

    Returns:
        Formatted list of test case versions or error message
    """
    if not zephyr_client:
        return format_error_message(
            "Get Test Case Versions", "Client not initialized", _CONFIG_ERROR_MSG
        )

    # Validate test case key
    test_case_validation = validate_test_case_key(test_case_key)
    if not test_case_validation.is_valid:
        return format_error_message(
            "Get Test Case Versions",
            "Invalid test case key",
            "; ".join(test_case_validation.errors),
        )

    # Get versions via API
    result = await zephyr_client.get_test_case_versions(
        test_case_key=test_case_key, max_results=max_results, start_at=start_at
    )

    if result.is_valid:
        return format_test_case_versions_list(result.data, test_case_key)
    else:
        return format_error_message(
            "Get Test Case Versions",
            f"Failed to retrieve versions for test case {test_case_key}",
            "; ".join(result.errors),
        )


@mcp.tool()
async def get_test_case_version(test_case_key: str, version: int) -> str:
    """Get a specific version of a test case in Zephyr Scale Cloud.

    Args:
        test_case_key: The key of the test case (format: [PROJECT]-T[NUMBER])
        version: Version number to retrieve

    Returns:
        Formatted test case information for the specific version or error message
    """
    if not zephyr_client:
        return format_error_message(
            "Get Test Case Version", "Client not initialized", _CONFIG_ERROR_MSG
        )

    # Validate test case key
    test_case_validation = validate_test_case_key(test_case_key)
    if not test_case_validation.is_valid:
        return format_error_message(
            "Get Test Case Version",
            "Invalid test case key",
            "; ".join(test_case_validation.errors),
        )

    # Validate version number
    version_validation = validate_version_number(version)
    if not version_validation.is_valid:
        return format_error_message(
            "Get Test Case Version",
            "Invalid version number",
            "; ".join(version_validation.errors),
        )

    # Get specific version via API
    result = await zephyr_client.get_test_case_version(
        test_case_key=test_case_key, version=version
    )

    if result.is_valid:
        # Add version info to the display
        version_note = f"📋 **Test Case Version {version}** for {test_case_key}\n\n"
        return version_note + format_test_case_display(result.data)
    else:
        return format_error_message(
            "Get Test Case Version",
            f"Failed to retrieve version {version} for test case {test_case_key}",
            "; ".join(result.errors),
        )


@mcp.tool()
async def get_links(test_case_key: str) -> str:
    """Get all links (issues + web links) for a test case in Zephyr Scale Cloud.

    Args:
        test_case_key: The key of the test case (format: [PROJECT]-T[NUMBER])

    Returns:
        Formatted list of links or error message
    """
    if not zephyr_client:
        return format_error_message(
            "Get Links", "Client not initialized", _CONFIG_ERROR_MSG
        )

    # Validate test case key
    test_case_validation = validate_test_case_key(test_case_key)
    if not test_case_validation.is_valid:
        return format_error_message(
            "Get Links",
            "Invalid test case key",
            "; ".join(test_case_validation.errors),
        )

    # Get links via API
    result = await zephyr_client.get_test_case_links(test_case_key=test_case_key)

    if result.is_valid:
        return format_test_case_links_display(result.data, test_case_key)
    else:
        return format_error_message(
            "Get Links",
            f"Failed to retrieve links for test case {test_case_key}",
            "; ".join(result.errors),
        )


@mcp.tool()
async def create_issue_link(test_case_key: str, issue_id: int) -> str:
    """Create a link between a test case and a Jira issue in Zephyr Scale Cloud.

    Args:
        test_case_key: The key of the test case (format: [PROJECT]-T[NUMBER])
        issue_id: The numeric Jira issue ID to link to (NOT the issue key)
                  Use the Atlassian/Jira MCP tool to get the issue ID from a key

    Returns:
        Success message with created link ID or error message
    """
    if not zephyr_client:
        return format_error_message(
            "Create Issue Link", "Client not initialized", _CONFIG_ERROR_MSG
        )

    # Validate test case key
    test_case_validation = validate_test_case_key(test_case_key)
    if not test_case_validation.is_valid:
        return format_error_message(
            "Create Issue Link",
            "Invalid test case key",
            "; ".join(test_case_validation.errors),
        )

    # Validate issue ID
    issue_id_validation = validate_issue_id(issue_id)
    if not issue_id_validation.is_valid:
        return format_error_message(
            "Create Issue Link",
            "Invalid issue ID",
            "; ".join(issue_id_validation.errors),
        )

    # Validate issue link input
    issue_link_data = {"issueId": issue_id}
    validation_result = validate_issue_link_input(issue_link_data)
    if not validation_result.is_valid:
        return format_error_message(
            "Create Issue Link",
            "Invalid issue link data",
            "; ".join(validation_result.errors),
        )

    # Create issue link via API
    result = await zephyr_client.create_test_case_issue_link(
        test_case_key=test_case_key, issue_link_input=validation_result.data
    )

    if result.is_valid:
        return format_success_message(
            "Issue Link Created",
            f"Successfully created issue link between test case {test_case_key} "
            f"and Jira issue {issue_id}",
            resource_id=result.data.id,
        )
    else:
        return format_error_message(
            "Create Issue Link",
            f"Failed to create issue link for test case {test_case_key}",
            "; ".join(result.errors),
        )


@mcp.tool()
async def create_web_link(test_case_key: str, url: str, description: str = None) -> str:
    """Create a link between a test case and a web URL in Zephyr Scale Cloud.

    Args:
        test_case_key: The key of the test case (format: [PROJECT]-T[NUMBER])
        url: The web URL to link to
        description: Optional description for the link

    Returns:
        Success message with created link ID or error message
    """
    if not zephyr_client:
        return format_error_message(
            "Create Web Link", "Client not initialized", _CONFIG_ERROR_MSG
        )

    # Validate test case key
    test_case_validation = validate_test_case_key(test_case_key)
    if not test_case_validation.is_valid:
        return format_error_message(
            "Create Web Link",
            "Invalid test case key",
            "; ".join(test_case_validation.errors),
        )

    # Validate web link input
    web_link_data = {"url": url}
    if description is not None:
        web_link_data["description"] = description

    validation_result = validate_web_link_input(web_link_data)
    if not validation_result.is_valid:
        return format_error_message(
            "Create Web Link",
            "Invalid web link data",
            "; ".join(validation_result.errors),
        )

    # Create web link via API
    result = await zephyr_client.create_test_case_web_link(
        test_case_key=test_case_key, web_link_input=validation_result.data
    )

    if result.is_valid:
        desc_text = f" ({description})" if description else ""
        return format_success_message(
            "Web Link Created",
            f"Successfully created web link between test case {test_case_key} "
            f"and {url}{desc_text}",
            resource_id=result.data.id,
        )
    else:
        return format_error_message(
            "Create Web Link",
            f"Failed to create web link for test case {test_case_key}",
            "; ".join(result.errors),
        )


@mcp.tool()
async def create_test_case(
    project_key: str,
    name: str,
    objective: str = None,
    precondition: str = None,
    estimated_time: int = None,
    component_id: int = None,
    priority_name: str = None,
    status_name: str = None,
    folder_id: int = None,
    owner_id: str = None,
    labels: list[str] = None,
    custom_fields: dict = None,
) -> str:
    """Create a new test case in Zephyr Scale Cloud.

    Args:
        project_key: Jira project key (e.g., 'PROJ')
        name: Test case name
        objective: Test case objective (optional)
        precondition: Test case preconditions (optional)
        estimated_time: Estimated duration in milliseconds (optional)
        component_id: Jira component ID (optional)
        priority_name: Priority name, defaults to 'Normal' (optional)
        status_name: Status name, defaults to 'Draft' (optional)
        folder_id: Folder ID to place the test case (optional)
        owner_id: Jira user account ID for owner (optional)
        labels: List of labels for the test case (optional)
        custom_fields: Custom fields dictionary (optional)

    Returns:
        Success message with created test case details or error message
    """
    if not zephyr_client:
        return format_error_message(
            "Create Test Case", "Client not initialized", _CONFIG_ERROR_MSG
        )

    # Validate project key
    project_validation = validate_project_key(project_key)
    if not project_validation.is_valid:
        return format_error_message(
            "Create Test Case",
            "Invalid project key",
            "; ".join(project_validation.errors),
        )

    # Validate test case name
    name_validation = validate_test_case_name(name)
    if not name_validation.is_valid:
        return format_error_message(
            "Create Test Case",
            "Invalid test case name",
            "; ".join(name_validation.errors),
        )

    # Build test case data
    test_case_data = {
        "projectKey": project_key,
        "name": name_validation.data,
    }

    # Add optional fields with validation
    if objective is not None:
        test_case_data["objective"] = objective

    if precondition is not None:
        test_case_data["precondition"] = precondition

    if estimated_time is not None:
        time_validation = validate_estimated_time(estimated_time)
        if not time_validation.is_valid:
            return format_error_message(
                "Create Test Case",
                "Invalid estimated time",
                "; ".join(time_validation.errors),
            )
        test_case_data["estimatedTime"] = time_validation.data

    if component_id is not None:
        component_validation = validate_component_id(component_id)
        if not component_validation.is_valid:
            return format_error_message(
                "Create Test Case",
                "Invalid component ID",
                "; ".join(component_validation.errors),
            )
        test_case_data["componentId"] = component_validation.data

    if priority_name is not None:
        test_case_data["priorityName"] = priority_name

    if status_name is not None:
        test_case_data["statusName"] = status_name

    if folder_id is not None:
        folder_validation = validate_folder_id(folder_id)
        if not folder_validation.is_valid:
            return format_error_message(
                "Create Test Case",
                "Invalid folder ID",
                "; ".join(folder_validation.errors),
            )
        test_case_data["folderId"] = folder_validation.data

    if owner_id is not None:
        test_case_data["ownerId"] = owner_id

    if labels is not None:
        test_case_data["labels"] = labels

    if custom_fields is not None:
        test_case_data["customFields"] = custom_fields

    # Validate complete test case input
    validation_result = validate_test_case_input(test_case_data)
    if not validation_result.is_valid:
        return format_error_message(
            "Create Test Case",
            "Invalid test case data",
            "; ".join(validation_result.errors),
        )

    # Create test case via API
    result = await zephyr_client.create_test_case(
        test_case_input=validation_result.data
    )

    if result.is_valid:
        return format_test_case_creation_success(result.data, project_key)
    else:
        return format_error_message(
            "Create Test Case",
            f"Failed to create test case in project {project_key}",
            "; ".join(result.errors),
        )


def main():
    """Run the MCP server.

    This starts the MCP server that AI assistants can connect to.
    """
    mcp.run()


if __name__ == "__main__":
    main()
