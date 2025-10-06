"""Enhanced MCP Server for Zephyr Scale Cloud with Pydantic schemas.

This file contains the Model Context Protocol (MCP) SERVER implementation
using Pydantic schemas for validation and type safety.
"""

import json
import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from mcp.server import FastMCP

from .clients.zephyr_client import ZephyrClient
from .config import ZephyrConfig
from .utils.validation import (
    validate_component_id,
    validate_estimated_time,
    validate_folder_data,
    validate_folder_id,
    validate_folder_type,
    validate_issue_id,
    validate_issue_link_input,
    validate_jira_version_id,
    validate_priority_data,
    validate_project_key,
    validate_status_data,
    validate_status_type,
    validate_test_case_input,
    validate_test_case_key,
    validate_test_case_name,
    validate_test_case_update_input,
    validate_test_cycle_input,
    validate_test_cycle_key,
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


def get_project_key_with_default(provided_key: str | None = None) -> str | None:
    """
    Get project key using provided value or default from environment.

    Args:
        provided_key: Project key provided by user (optional)

    Returns:
        Project key to use, or None if neither provided nor default available
    """
    if provided_key:
        return provided_key

    # Try to get default from environment
    default_key = os.getenv("ZEPHYR_SCALE_DEFAULT_PROJECT_KEY")

    return default_key


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

    if result.is_valid:
        # Healthcheck endpoint returns 200 OK with no content according to API spec
        return json.dumps({"status": "UP"}, indent=2)
    else:
        return json.dumps(
            {
                "errorCode": 500,
                "message": (
                    "; ".join(result.errors) if result.errors else "Health check failed"
                ),
            },
            indent=2,
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

    # Get project key with default fallback
    project_key = get_project_key_with_default(project_key)

    # Validate project key if provided
    if project_key:
        project_validation = validate_project_key(project_key)
        if not project_validation.is_valid:
            return json.dumps(
                {"errorCode": 400, "message": "; ".join(project_validation.errors)},
                indent=2,
            )

    result = await zephyr_client.get_priorities(
        project_key=project_key, max_results=max_results
    )

    if result.is_valid:
        # Returns PriorityList schema according to API spec
        return json.dumps(
            result.data.model_dump(by_alias=True, exclude_none=True), indent=2
        )
    else:
        return json.dumps(
            {
                "errorCode": 500,
                "message": (
                    "; ".join(result.errors)
                    if result.errors
                    else "Failed to retrieve priorities"
                ),
            },
            indent=2,
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
        # Returns Priority schema according to API spec
        return json.dumps(
            result.data.model_dump(by_alias=True, exclude_none=True), indent=2
        )
    else:
        return json.dumps(
            {
                "errorCode": 404,
                "message": f"Priority '{priority_id}' does not exist or you do not "
                f"have access to it",
            },
            indent=2,
        )


@mcp.tool()
async def create_priority(
    name: str,
    project_key: str | None = None,
    description: str | None = None,
    color: str | None = None,
) -> str:
    """
    Create a new priority in Zephyr Scale Cloud.

    Args:
        name: Name of the priority (max 255 characters)
        project_key: Jira project key (optional, uses ZEPHYR_SCALE_DEFAULT_PROJECT_KEY
                     if not provided)
        description: Optional description of the priority (max 255 characters)
        color: Optional color code for the priority (e.g., '#FF0000')

    Returns:
        str: Result of the priority creation
    """
    if not zephyr_client:
        return _CONFIG_ERROR_MSG

    # Get project key with default fallback
    project_key = get_project_key_with_default(project_key)

    # Validate project key (required for CREATE operations)
    project_validation = validate_project_key(project_key)
    if not project_validation.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(project_validation.errors)},
            indent=2,
        )

    # Validate input data using Pydantic schema
    request_data = {
        "projectKey": project_key,
        "name": name,
        "description": description,
        "color": color,
    }

    validation_result = validate_priority_data(request_data, is_update=False)
    if not validation_result:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(validation_result.errors)}, indent=2
        )

    # Create priority using validated schema
    result = await zephyr_client.create_priority(validation_result.data)

    if result.is_valid:
        # Returns CreatedResource schema according to API spec
        return json.dumps(
            result.data.model_dump(by_alias=True, exclude_none=True), indent=2
        )
    else:
        return json.dumps(
            {
                "errorCode": 400,
                "message": (
                    "; ".join(result.errors)
                    if result.errors
                    else "Failed to create priority"
                ),
            },
            indent=2,
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
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(validation_result.errors)}, indent=2
        )

    # Update priority using validated schema
    result = await zephyr_client.update_priority(priority_id, validation_result.data)

    if result.is_valid:
        # Update operations return 200 OK with no content according to API spec
        return json.dumps({"status": "updated"}, indent=2)
    else:
        return json.dumps(
            {
                "errorCode": 400,
                "message": (
                    "; ".join(result.errors)
                    if result.errors
                    else f"Failed to update priority {priority_id}"
                ),
            },
            indent=2,
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
            return json.dumps(
                {"errorCode": 400, "message": "; ".join(type_validation.errors)},
                indent=2,
            )

        # Import here to avoid circular imports
        from .schemas.status import StatusType

        parsed_status_type = StatusType(status_type)

    # Get project key with default fallback
    project_key = get_project_key_with_default(project_key)

    # Validate project key if provided
    if project_key:
        project_validation = validate_project_key(project_key)
        if not project_validation.is_valid:
            return json.dumps(
                {"errorCode": 400, "message": "; ".join(project_validation.errors)},
                indent=2,
            )

    result = await zephyr_client.get_statuses(
        project_key=project_key,
        status_type=parsed_status_type,
        max_results=max_results,
    )

    if result.is_valid:
        # Returns StatusList schema according to API spec
        return json.dumps(
            result.data.model_dump(by_alias=True, exclude_none=True), indent=2
        )
    else:
        return json.dumps(
            {
                "errorCode": 500,
                "message": (
                    "; ".join(result.errors)
                    if result.errors
                    else "Failed to retrieve statuses"
                ),
            },
            indent=2,
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
        return json.dumps(
            {"errorCode": 400, "message": "Status ID must be a positive integer"},
            indent=2,
        )

    result = await zephyr_client.get_status(status_id)

    if result.is_valid:
        # Returns Status schema according to API spec
        return json.dumps(
            result.data.model_dump(by_alias=True, exclude_none=True), indent=2
        )
    else:
        return json.dumps(
            {
                "errorCode": 404,
                "message": f"Status '{status_id}' does not exist or you do not have "
                f"access to it",
            },
            indent=2,
        )


@mcp.tool()
async def create_status(
    name: str,
    status_type: str,
    project_key: str | None = None,
    description: str | None = None,
    color: str | None = None,
) -> str:
    """
    Create a new status in Zephyr Scale Cloud.

    Args:
        name: Name of the status (max 255 characters)
        status_type: Status type ('TEST_CASE', 'TEST_PLAN', 'TEST_CYCLE',
                             'TEST_EXECUTION')
        project_key: Jira project key (optional, uses
                     ZEPHYR_SCALE_DEFAULT_PROJECT_KEY if not provided)
        description: Optional description of the status (max 255 characters)
        color: Optional color code for the status (e.g., '#FF0000')

    Returns:
        str: Result of the status creation
    """
    if not zephyr_client:
        return _CONFIG_ERROR_MSG

    # Get project key with default fallback
    project_key = get_project_key_with_default(project_key)

    # Validate project key (required for CREATE operations)
    project_validation = validate_project_key(project_key)
    if not project_validation.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(project_validation.errors)},
            indent=2,
        )

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
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(validation_result.errors)}, indent=2
        )

    # Create status using validated schema
    result = await zephyr_client.create_status(validation_result.data)

    if result.is_valid:
        # Returns CreatedResource schema according to API spec
        return json.dumps(
            result.data.model_dump(by_alias=True, exclude_none=True), indent=2
        )
    else:
        return json.dumps(
            {
                "errorCode": 400,
                "message": (
                    "; ".join(result.errors)
                    if result.errors
                    else "Failed to create status"
                ),
            },
            indent=2,
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
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(validation_result.errors)}, indent=2
        )

    # Update status using validated schema
    result = await zephyr_client.update_status(status_id, validation_result.data)

    if result.is_valid:
        # Update operations return 200 OK with no content according to API spec
        return json.dumps({"status": "updated"}, indent=2)
    else:
        return json.dumps(
            {
                "errorCode": 400,
                "message": (
                    "; ".join(result.errors)
                    if result.errors
                    else f"Failed to update status {status_id}"
                ),
            },
            indent=2,
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
        return _CONFIG_ERROR_MSG

    # Validate folder type if provided
    validated_folder_type = None
    if folder_type:
        folder_type_result = validate_folder_type(folder_type)
        if not folder_type_result.is_valid:
            return json.dumps(
                {"errorCode": 400, "message": "; ".join(folder_type_result.errors)},
                indent=2,
            )
        validated_folder_type = folder_type_result.data

    # Get project key with default fallback
    project_key = get_project_key_with_default(project_key)

    # Validate project key if provided
    if project_key:
        project_key_result = validate_project_key(project_key)
        if not project_key_result.is_valid:
            return json.dumps(
                {"errorCode": 400, "message": "; ".join(project_key_result.errors)},
                indent=2,
            )

    # Get folders from API
    result = await zephyr_client.get_folders(
        project_key=project_key,
        folder_type=validated_folder_type,
        max_results=max_results,
    )

    if result.is_valid:
        # Returns FolderList schema according to API spec
        return json.dumps(
            result.data.model_dump(by_alias=True, exclude_none=True), indent=2
        )
    else:
        return json.dumps(
            {
                "errorCode": 500,
                "message": (
                    "; ".join(result.errors)
                    if result.errors
                    else "Failed to retrieve folders"
                ),
            },
            indent=2,
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
        return _CONFIG_ERROR_MSG

    if folder_id < 1:
        return json.dumps(
            {"errorCode": 400, "message": "Folder ID must be a positive integer"},
            indent=2,
        )

    # Get folder from API
    result = await zephyr_client.get_folder(folder_id)

    if result.is_valid:
        # Returns Folder schema according to API spec
        return json.dumps(
            result.data.model_dump(by_alias=True, exclude_none=True), indent=2
        )
    else:
        return json.dumps(
            {
                "errorCode": 404,
                "message": f"Folder '{folder_id}' does not exist or you do not have "
                f"access to it",
            },
            indent=2,
        )


@mcp.tool()
async def create_folder(
    name: str,
    folder_type: str,
    project_key: str | None = None,
    parent_id: str | None = None,
) -> str:
    """Create a new folder in Zephyr Scale Cloud.

    Args:
        name: Folder name (1-255 characters)
        folder_type: Folder type (TEST_CASE, TEST_PLAN, TEST_CYCLE)
        project_key: Jira project key (optional, uses
                     ZEPHYR_SCALE_DEFAULT_PROJECT_KEY if not provided)
        parent_id: Optional parent folder ID as string (null for root folders)

    Returns:
        Success message with created folder ID or error message
    """
    # Convert and validate parent_id if provided
    parsed_parent_id = None
    if parent_id is not None:
        try:
            parsed_parent_id = int(parent_id)
            # Use validation utility instead of inline validation
            validation = validate_folder_id(parsed_parent_id)
            if not validation.is_valid:
                return json.dumps(
                    {"errorCode": 400, "message": "; ".join(validation.errors)},
                    indent=2,
                )
        except (ValueError, TypeError):
            return json.dumps(
                {
                    "errorCode": 400,
                    "message": f"Parent folder ID must be a valid integer, "
                    f"got: {parent_id}",
                },
                indent=2,
            )

    if not zephyr_client:
        return _CONFIG_ERROR_MSG

    # Get project key with default fallback
    project_key = get_project_key_with_default(project_key)

    # Validate project key (required for CREATE operations)
    project_validation = validate_project_key(project_key)
    if not project_validation.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(project_validation.errors)},
            indent=2,
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
        return json.dumps(
            {"errorCode": 400, "message": validation_result.error_message}, indent=2
        )

    # Create folder via API
    result = await zephyr_client.create_folder(validation_result.data)

    if result.is_valid:
        # Returns CreatedResource schema according to API spec
        return json.dumps(
            result.data.model_dump(by_alias=True, exclude_none=True), indent=2
        )
    else:
        return json.dumps(
            {
                "errorCode": 400,
                "message": (
                    "; ".join(result.errors)
                    if result.errors
                    else f"Failed to create folder '{name}'"
                ),
            },
            indent=2,
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
        return _CONFIG_ERROR_MSG

    # Validate test case key
    test_case_validation = validate_test_case_key(test_case_key)
    if not test_case_validation.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(test_case_validation.errors)},
            indent=2,
        )

    # Get test steps from API
    result = await zephyr_client.get_test_steps(
        test_case_key=test_case_key,
        max_results=max_results,
        start_at=start_at,
    )

    if result.is_valid:
        # Returns TestStepsList schema according to API spec
        return json.dumps(
            result.data.model_dump(by_alias=True, exclude_none=True), indent=2
        )
    else:
        return json.dumps(
            {
                "errorCode": 404,
                "message": f"Test case '{test_case_key}' does not exist or you do not "
                f"have access to it",
            },
            indent=2,
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
        return _CONFIG_ERROR_MSG

    # Validate test case key
    test_case_validation = validate_test_case_key(test_case_key)
    if not test_case_validation.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(test_case_validation.errors)},
            indent=2,
        )

    # Validate mode
    mode_validation = validate_test_steps_mode(mode)
    if not mode_validation.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(mode_validation.errors)}, indent=2
        )

    # Parse and validate steps JSON
    try:
        steps_data = json.loads(steps)
        if not isinstance(steps_data, list):
            return json.dumps(
                {"errorCode": 400, "message": "Steps must be a JSON array"}, indent=2
            )
    except json.JSONDecodeError as e:
        return json.dumps(
            {"errorCode": 400, "message": f"Failed to parse steps JSON: {str(e)}"},
            indent=2,
        )

    # Build and validate test steps input
    test_steps_input_data = {
        "mode": mode_validation.data,
        "items": steps_data,
    }

    validation_result = validate_test_steps_input(test_steps_input_data)
    if not validation_result.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(validation_result.errors)}, indent=2
        )

    # Create test steps via API
    result = await zephyr_client.create_test_steps(
        test_case_key=test_case_key,
        test_steps_input=validation_result.data,
    )

    if result.is_valid:
        # Returns CreatedResource schema according to API spec
        return json.dumps(
            result.data.model_dump(by_alias=True, exclude_none=True), indent=2
        )
    else:
        return json.dumps(
            {
                "errorCode": 400,
                "message": (
                    "; ".join(result.errors)
                    if result.errors
                    else f"Failed to create test steps for {test_case_key}"
                ),
            },
            indent=2,
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
        return _CONFIG_ERROR_MSG

    # Validate test case key
    test_case_validation = validate_test_case_key(test_case_key)
    if not test_case_validation.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(test_case_validation.errors)},
            indent=2,
        )

    # Get test script via API
    result = await zephyr_client.get_test_script(test_case_key=test_case_key)

    if result.is_valid:
        # Returns TestScript schema according to API spec
        return json.dumps(
            result.data.model_dump(by_alias=True, exclude_none=True), indent=2
        )
    else:
        return json.dumps(
            {
                "errorCode": 404,
                "message": f"Test case '{test_case_key}' does not exist or you do not "
                f"have access to it",
            },
            indent=2,
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
        return _CONFIG_ERROR_MSG

    # Validate test case key
    test_case_validation = validate_test_case_key(test_case_key)
    if not test_case_validation.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(test_case_validation.errors)},
            indent=2,
        )

    # Validate script type
    type_validation = validate_test_script_type(script_type)
    if not type_validation.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(type_validation.errors)}, indent=2
        )

    # Build and validate test script input
    test_script_input_data = {
        "type": type_validation.data,
        "text": text,
    }

    validation_result = validate_test_script_input(test_script_input_data)
    if not validation_result.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(validation_result.errors)}, indent=2
        )

    # Create test script via API
    result = await zephyr_client.create_test_script(
        test_case_key=test_case_key,
        test_script_input=validation_result.data,
    )

    if result.is_valid:
        # Returns CreatedResource schema according to API spec
        return json.dumps(
            result.data.model_dump(by_alias=True, exclude_none=True), indent=2
        )
    else:
        return json.dumps(
            {
                "errorCode": 400,
                "message": (
                    "; ".join(result.errors)
                    if result.errors
                    else f"Failed to create test script for {test_case_key}"
                ),
            },
            indent=2,
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
        return _CONFIG_ERROR_MSG

    # Validate test case key
    test_case_validation = validate_test_case_key(test_case_key)
    if not test_case_validation.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(test_case_validation.errors)},
            indent=2,
        )

    # Get test case via API
    result = await zephyr_client.get_test_case(test_case_key=test_case_key)

    if result.is_valid:
        # Returns TestCase schema according to API spec
        return json.dumps(
            result.data.model_dump(by_alias=True, exclude_none=True, mode="json"),
            indent=2,
        )
    else:
        return json.dumps(
            {
                "errorCode": 404,
                "message": f"Test case '{test_case_key}' does not exist or you do not "
                f"have access to it",
            },
            indent=2,
        )


@mcp.tool()
async def get_test_cases(
    project_key: str | None = None,
    folder_id: str | None = None,
    max_results: int = 10,
    start_at: int = 0,
) -> str:
    """Get test cases using traditional offset-based pagination.

    This tool uses the stable /testcases endpoint that provides reliable
    offset-based pagination for retrieving test cases.

    📖 OFFSET-BASED PAGINATION GUIDE:
    Offset pagination works like pages in a book - you specify which "page" to start
    reading from and how many items per "page".

    🔢 HOW TO PAGINATE THROUGH ALL RESULTS:
    1. FIRST REQUEST: start_at=0, max_results=1000 (gets items 0-999)
    2. NEXT REQUEST: start_at=1000, max_results=1000 (gets items 1000-1999)
    3. CONTINUE: start_at=2000, max_results=1000 (gets items 2000-2999)
    4. STOP when response has fewer items than max_results

    💡 PAGINATION FORMULA:
    - Next start_at = current_start_at + max_results
    - Example: If start_at=0 and max_results=1000, next start_at=1000
    - Always ensure start_at is a multiple of max_results (as per API docs)

    ⚡ PERFORMANCE TIP:
    Use max_results=1000 (maximum allowed) for fastest data retrieval.
    The API default is only 10, which is very slow for large datasets.

    🛑 IMPORTANT:
    - start_at should be a multiple of max_results (API requirement)
    - Check response length vs max_results to detect the last page
    - Server may return fewer results than requested due to constraints

    Args:
        project_key: Jira project key filter (e.g., 'PROJ'). If you have access to
                    more than 1000 projects, this parameter may be mandatory.
                    Uses ZEPHYR_SCALE_DEFAULT_PROJECT_KEY if not provided
        folder_id: ID of a folder to filter test cases (optional)
        max_results: Maximum number of results to return (default: 10, max: 1000).
                    RECOMMENDATION: Use 1000 for fastest bulk data retrieval.
        start_at: Zero-indexed starting position (default: 0).
                 MUST be a multiple of max_results.
                 For next page: start_at + max_results

    Returns:
        JSON response with test cases and pagination information.
        Check if len(values) < max_results to detect the last page.
    """
    if not zephyr_client:
        return _CONFIG_ERROR_MSG

    # Get project key with default fallback
    project_key = get_project_key_with_default(project_key)

    # Validate project key if provided
    if project_key:
        project_key_result = validate_project_key(project_key)
        if not project_key_result.is_valid:
            return json.dumps(
                {"errorCode": 400, "message": "; ".join(project_key_result.errors)},
                indent=2,
            )

    # Validate folder_id parameter
    resolved_folder_id = None
    if folder_id is not None:
        try:
            resolved_folder_id = int(folder_id)
            if resolved_folder_id < 1:
                return json.dumps(
                    {
                        "errorCode": 400,
                        "message": "folder_id must be a positive integer",
                    },
                    indent=2,
                )
        except ValueError:
            return json.dumps(
                {
                    "errorCode": 400,
                    "message": "folder_id must be a valid integer",
                },
                indent=2,
            )

    # Call the client
    result = await zephyr_client.get_test_cases(
        project_key=project_key,
        folder_id=resolved_folder_id,
        max_results=max_results,
        start_at=start_at,
    )

    if result.is_valid:
        # Return the paginated response
        return json.dumps(
            result.data.model_dump(by_alias=True, exclude_none=True, mode="json"),
            indent=2,
        )
    else:
        return json.dumps(
            {
                "errorCode": 400,
                "message": "; ".join(result.errors),
            },
            indent=2,
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
        return _CONFIG_ERROR_MSG

    # Validate test case key
    test_case_validation = validate_test_case_key(test_case_key)
    if not test_case_validation.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(test_case_validation.errors)},
            indent=2,
        )

    # Get versions via API
    result = await zephyr_client.get_test_case_versions(
        test_case_key=test_case_key, max_results=max_results, start_at=start_at
    )

    if result.is_valid:
        # Returns TestCaseVersionLinkList schema according to API spec
        return json.dumps(
            result.data.model_dump(by_alias=True, exclude_none=True), indent=2
        )
    else:
        return json.dumps(
            {
                "errorCode": 404,
                "message": f"Test case '{test_case_key}' does not exist or you do not "
                f"have access to it",
            },
            indent=2,
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
        return _CONFIG_ERROR_MSG

    # Validate test case key
    test_case_validation = validate_test_case_key(test_case_key)
    if not test_case_validation.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(test_case_validation.errors)},
            indent=2,
        )

    # Validate version number
    version_validation = validate_version_number(version)
    if not version_validation.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(version_validation.errors)},
            indent=2,
        )

    # Get specific version via API
    result = await zephyr_client.get_test_case_version(
        test_case_key=test_case_key, version=version
    )

    if result.is_valid:
        # Returns TestCase schema according to API spec
        return json.dumps(
            result.data.model_dump(by_alias=True, exclude_none=True, mode="json"),
            indent=2,
        )
    else:
        return json.dumps(
            {
                "errorCode": 404,
                "message": f"Test case '{test_case_key}' version {version} does not "
                f"exist or you do not have access to it",
            },
            indent=2,
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
        return _CONFIG_ERROR_MSG

    # Validate test case key
    test_case_validation = validate_test_case_key(test_case_key)
    if not test_case_validation.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(test_case_validation.errors)},
            indent=2,
        )

    # Get links via API
    result = await zephyr_client.get_test_case_links(test_case_key=test_case_key)

    if result.is_valid:
        # Returns TestCaseLinkList schema according to API spec
        return json.dumps(
            result.data.model_dump(by_alias=True, exclude_none=True), indent=2
        )
    else:
        return json.dumps(
            {
                "errorCode": 404,
                "message": f"Test case '{test_case_key}' does not exist or you do not "
                f"have access to it",
            },
            indent=2,
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
        return _CONFIG_ERROR_MSG

    # Validate test case key
    test_case_validation = validate_test_case_key(test_case_key)
    if not test_case_validation.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(test_case_validation.errors)},
            indent=2,
        )

    # Validate issue ID
    issue_id_validation = validate_issue_id(issue_id)
    if not issue_id_validation.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(issue_id_validation.errors)},
            indent=2,
        )

    # Validate issue link input
    issue_link_data = {"issueId": issue_id}
    validation_result = validate_issue_link_input(issue_link_data)
    if not validation_result.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(validation_result.errors)}, indent=2
        )

    # Create issue link via API
    result = await zephyr_client.create_test_case_issue_link(
        test_case_key=test_case_key, issue_link_input=validation_result.data
    )

    if result.is_valid:
        # Returns CreatedResource schema according to API spec
        return json.dumps(
            result.data.model_dump(by_alias=True, exclude_none=True), indent=2
        )
    else:
        return json.dumps(
            {
                "errorCode": 400,
                "message": (
                    "; ".join(result.errors)
                    if result.errors
                    else f"Failed to create issue link for test case {test_case_key}"
                ),
            },
            indent=2,
        )


@mcp.tool()
async def create_web_link(
    test_case_key: str, url: str, description: str | None = None
) -> str:
    """Create a link between a test case and a web URL in Zephyr Scale Cloud.

    Args:
        test_case_key: The key of the test case (format: [PROJECT]-T[NUMBER])
        url: The web URL to link to
        description: Optional description for the link

    Returns:
        Success message with created link ID or error message
    """
    if not zephyr_client:
        return _CONFIG_ERROR_MSG

    # Validate test case key
    test_case_validation = validate_test_case_key(test_case_key)
    if not test_case_validation.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(test_case_validation.errors)},
            indent=2,
        )

    # Validate web link input
    web_link_data = {"url": url}
    if description is not None:
        web_link_data["description"] = description

    validation_result = validate_web_link_input(web_link_data)
    if not validation_result.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(validation_result.errors)}, indent=2
        )

    # Create web link via API
    result = await zephyr_client.create_test_case_web_link(
        test_case_key=test_case_key, web_link_input=validation_result.data
    )

    if result.is_valid:
        # Returns CreatedResource schema according to API spec
        return json.dumps(
            result.data.model_dump(by_alias=True, exclude_none=True), indent=2
        )
    else:
        return json.dumps(
            {
                "errorCode": 400,
                "message": (
                    "; ".join(result.errors)
                    if result.errors
                    else f"Failed to create web link for test case {test_case_key}"
                ),
            },
            indent=2,
        )


@mcp.tool()
async def create_test_case(
    name: str,
    project_key: str | None = None,
    objective: str | None = None,
    precondition: str | None = None,
    estimated_time: str | None = None,
    component_id: str | None = None,
    priority_name: str | None = None,
    status_name: str | None = None,
    folder_id: str | None = None,
    owner_id: str | None = None,
    labels: str | None = None,
    custom_fields: str | dict | None = None,
) -> str:
    """Create a new test case in Zephyr Scale Cloud.

    Args:
        name: Test case name
        project_key: Jira project key (optional, uses
                     ZEPHYR_SCALE_DEFAULT_PROJECT_KEY if not provided)
        objective: Test case objective (optional)
        precondition: Test case preconditions (optional)
        estimated_time: Estimated duration in milliseconds as string (optional)
        component_id: Jira component ID as string (optional)
        priority_name: Priority name, defaults to 'Normal' (optional)
        status_name: Status name, defaults to 'Draft' (optional)
        folder_id: Folder ID as string to place the test case (optional)
        owner_id: Jira user account ID for owner (optional)
        labels: Labels as JSON array string (e.g., '["automation", "smoke"]') or
                comma-separated (e.g., "automation, smoke") (optional)
        custom_fields: Custom fields as JSON string or dict (e.g.,
                      '{"Components": ["Update"], "Version": "v1.0.0"}' or
                      {"Components": ["Update"], "Version": "v1.0.0"}) (optional)

    Returns:
        Success message with created test case details or error message
    """
    if not zephyr_client:
        return _CONFIG_ERROR_MSG

    # Get project key with default fallback
    project_key = get_project_key_with_default(project_key)

    # Validate project key (required for CREATE operations)
    project_validation = validate_project_key(project_key)
    if not project_validation.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(project_validation.errors)},
            indent=2,
        )

    # Validate test case name
    name_validation = validate_test_case_name(name)
    if not name_validation.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(name_validation.errors)}, indent=2
        )

    # Convert and validate integer parameters
    parsed_estimated_time = None
    if estimated_time is not None:
        try:
            parsed_estimated_time = int(estimated_time)
            # Use validation utility instead of inline validation
            validation = validate_estimated_time(parsed_estimated_time)
            if not validation.is_valid:
                return json.dumps(
                    {"errorCode": 400, "message": "; ".join(validation.errors)},
                    indent=2,
                )
        except (ValueError, TypeError):
            return json.dumps(
                {
                    "errorCode": 400,
                    "message": f"Estimated time must be a valid integer, "
                    f"got: {estimated_time}",
                },
                indent=2,
            )

    parsed_component_id = None
    if component_id is not None:
        try:
            parsed_component_id = int(component_id)
            # Use validation utility instead of inline validation
            validation = validate_component_id(parsed_component_id)
            if not validation.is_valid:
                return json.dumps(
                    {"errorCode": 400, "message": "; ".join(validation.errors)},
                    indent=2,
                )
        except (ValueError, TypeError):
            return json.dumps(
                {
                    "errorCode": 400,
                    "message": f"Component ID must be a valid integer, "
                    f"got: {component_id}",
                },
                indent=2,
            )

    parsed_folder_id = None
    if folder_id is not None:
        try:
            parsed_folder_id = int(folder_id)
            # Use validation utility instead of inline validation
            validation = validate_folder_id(parsed_folder_id)
            if not validation.is_valid:
                return json.dumps(
                    {"errorCode": 400, "message": "; ".join(validation.errors)},
                    indent=2,
                )
        except (ValueError, TypeError):
            return json.dumps(
                {
                    "errorCode": 400,
                    "message": f"Folder ID must be a valid integer, got: {folder_id}",
                },
                indent=2,
            )

    # Convert and validate labels
    parsed_labels = None
    if labels is not None:
        try:
            # Try JSON array format first
            parsed_labels = json.loads(labels)
            if not isinstance(parsed_labels, list):
                return json.dumps(
                    {
                        "errorCode": 400,
                        "message": "Labels must be a JSON array (e.g., "
                        '\'["automation", "smoke"]\') or comma-separated string',
                    },
                    indent=2,
                )
            # Validate all items are strings
            for item in parsed_labels:
                if not isinstance(item, str):
                    return json.dumps(
                        {"errorCode": 400, "message": "All labels must be strings"},
                        indent=2,
                    )
        except json.JSONDecodeError:
            # Fall back to comma-separated format
            try:
                parsed_labels = [
                    label.strip() for label in labels.split(",") if label.strip()
                ]
                if not parsed_labels:
                    return json.dumps(
                        {
                            "errorCode": 400,
                            "message": "Labels cannot be empty. Use JSON array "
                            "format or comma-separated values",
                        },
                        indent=2,
                    )
            except Exception as e:
                return json.dumps(
                    {
                        "errorCode": 400,
                        "message": f"Failed to parse labels: {str(e)}. Use JSON array "
                        'format (e.g., \'["label1", "label2"]\') or comma-separated '
                        "(e.g., 'label1, label2')",
                    },
                    indent=2,
                )

    # Convert and validate custom fields
    parsed_custom_fields = None
    if custom_fields is not None:
        if isinstance(custom_fields, dict):
            # Already a dictionary (parsed by MCP framework)
            parsed_custom_fields = custom_fields
        elif isinstance(custom_fields, str):
            # String input - parse as JSON
            try:
                parsed_custom_fields = json.loads(custom_fields)
                if not isinstance(parsed_custom_fields, dict):
                    return json.dumps(
                        {
                            "errorCode": 400,
                            "message": "Custom fields must be a JSON object (e.g., "
                            '\'{"Components": ["Update"], "Version": "v1.0.0"}\')',
                        },
                        indent=2,
                    )
            except json.JSONDecodeError as e:
                return json.dumps(
                    {
                        "errorCode": 400,
                        "message": f"Custom fields must be valid JSON: {str(e)}. "
                        'Example: \'{"Components": ["Update"], "Version": "v1.0.0"}\'',
                    },
                    indent=2,
                )
            except Exception as e:
                return json.dumps(
                    {
                        "errorCode": 400,
                        "message": f"Failed to parse custom fields: {str(e)}",
                    },
                    indent=2,
                )
        else:
            return json.dumps(
                {
                    "errorCode": 400,
                    "message": "Custom fields must be a JSON object or JSON string. "
                    'Example: \'{"Components": ["Update"], "Version": "v1.0.0"}\'',
                },
                indent=2,
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

    if parsed_estimated_time is not None:
        test_case_data["estimatedTime"] = parsed_estimated_time

    if parsed_component_id is not None:
        test_case_data["componentId"] = parsed_component_id

    if priority_name is not None:
        test_case_data["priorityName"] = priority_name

    if status_name is not None:
        test_case_data["statusName"] = status_name

    if parsed_folder_id is not None:
        test_case_data["folderId"] = parsed_folder_id

    if owner_id is not None:
        test_case_data["ownerId"] = owner_id

    if parsed_labels is not None:
        test_case_data["labels"] = parsed_labels

    if parsed_custom_fields is not None:
        test_case_data["customFields"] = parsed_custom_fields

    # Validate complete test case input
    validation_result = validate_test_case_input(test_case_data)
    if not validation_result.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(validation_result.errors)}, indent=2
        )

    # Create test case via API
    result = await zephyr_client.create_test_case(
        test_case_input=validation_result.data
    )

    if result.is_valid:
        # Returns CreatedResource schema according to API spec
        return json.dumps(
            result.data.model_dump(by_alias=True, exclude_none=True), indent=2
        )
    else:
        return json.dumps(
            {
                "errorCode": 400,
                "message": (
                    "; ".join(result.errors)
                    if result.errors
                    else f"Failed to create test case in project {project_key}"
                ),
            },
            indent=2,
        )


@mcp.tool()
async def update_test_case(
    test_case_key: str,
    name: str | None = None,
    objective: str | None = None,
    precondition: str | None = None,
    estimated_time: str | None = None,
    component_id: str | None = None,
    priority_id: str | None = None,
    status_id: str | None = None,
    folder_id: str | None = None,
    owner_id: str | None = None,
    labels: str | None = None,
    custom_fields: str | dict | None = None,
) -> str:
    """Update an existing test case in Zephyr Scale Cloud.

    Args:
        test_case_key: The key of the test case to update (format: [PROJECT]-T[NUMBER])
        name: Test case name (optional)
        objective: Test case objective (optional)
        precondition: Test case preconditions (optional)
        estimated_time: Estimated duration in milliseconds as string (optional)
        component_id: Jira component ID as string (optional)
        priority_id: Priority ID as string (optional, use get_priorities to find IDs)
        status_id: Status ID as string (optional, use get_statuses to find IDs)
        folder_id: Folder ID as string (optional, use get_folders to find IDs)
        owner_id: Jira user account ID for owner (optional)
        labels: Labels as JSON array string (e.g., '["automation", "smoke"]') or
                comma-separated (e.g., "automation, smoke") (optional)
        custom_fields: Custom fields as JSON string or dict (e.g.,
                      '{"Components": ["Update"], "Version": "v1.0.0"}' or
                      {"Components": ["Update"], "Version": "v1.0.0"}) (optional)

    Returns:
        Success message or error message
    """

    # Detect common mistakes where users try to pass names instead of IDs
    # and provide helpful error messages directing them to lookup tools
    def check_for_name_instead_of_id(param_name: str, param_value: str) -> str | None:
        """Check if parameter looks like name instead of ID, return error message."""
        try:
            int(param_value)
            return None  # It's a valid integer, not a name
        except (ValueError, TypeError):
            if param_name == "priority_id":
                return (
                    f"priority_id must be a numeric ID, got '{param_value}'. "
                    f"Use get_priorities tool to find priority IDs by name."
                )
            elif param_name == "status_id":
                return (
                    f"status_id must be a numeric ID, got '{param_value}'. "
                    f"Use get_statuses tool to find status IDs by name."
                )
            elif param_name == "folder_id":
                return (
                    f"folder_id must be a numeric ID, got '{param_value}'. "
                    f"Use get_folders tool to find folder IDs by name."
                )
            return f"{param_name} must be a numeric ID, got '{param_value}'."

    # Check for name-instead-of-ID mistakes early
    if priority_id is not None:
        error_msg = check_for_name_instead_of_id("priority_id", priority_id)
        if error_msg:
            return json.dumps({"errorCode": 400, "message": error_msg}, indent=2)

    if status_id is not None:
        error_msg = check_for_name_instead_of_id("status_id", status_id)
        if error_msg:
            return json.dumps({"errorCode": 400, "message": error_msg}, indent=2)

    if folder_id is not None:
        error_msg = check_for_name_instead_of_id("folder_id", folder_id)
        if error_msg:
            return json.dumps({"errorCode": 400, "message": error_msg}, indent=2)

    if not zephyr_client:
        return _CONFIG_ERROR_MSG

    # Validate test case key
    test_case_validation = validate_test_case_key(test_case_key)
    if not test_case_validation.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(test_case_validation.errors)},
            indent=2,
        )

    # Validate test case name if provided
    if name is not None:
        name_validation = validate_test_case_name(name)
        if not name_validation.is_valid:
            return json.dumps(
                {"errorCode": 400, "message": "; ".join(name_validation.errors)},
                indent=2,
            )

    # Convert and validate integer parameters
    parsed_estimated_time = None
    if estimated_time is not None:
        try:
            parsed_estimated_time = int(estimated_time)
            # Use validation utility
            validation = validate_estimated_time(parsed_estimated_time)
            if not validation.is_valid:
                return json.dumps(
                    {"errorCode": 400, "message": "; ".join(validation.errors)},
                    indent=2,
                )
        except (ValueError, TypeError):
            return json.dumps(
                {
                    "errorCode": 400,
                    "message": f"Estimated time must be a valid integer, "
                    f"got: {estimated_time}",
                },
                indent=2,
            )

    parsed_component_id = None
    if component_id is not None:
        try:
            parsed_component_id = int(component_id)
            # Use validation utility
            validation = validate_component_id(parsed_component_id)
            if not validation.is_valid:
                return json.dumps(
                    {"errorCode": 400, "message": "; ".join(validation.errors)},
                    indent=2,
                )
        except (ValueError, TypeError):
            return json.dumps(
                {
                    "errorCode": 400,
                    "message": f"Component ID must be a valid integer, "
                    f"got: {component_id}",
                },
                indent=2,
            )

    # Validate priority_id if provided
    parsed_priority_id = None
    if priority_id is not None:
        try:
            parsed_priority_id = int(priority_id)
            if parsed_priority_id <= 0:
                return json.dumps(
                    {
                        "errorCode": 400,
                        "message": f"Priority ID must be a positive integer, "
                        f"got: {priority_id}",
                    },
                    indent=2,
                )
        except (ValueError, TypeError):
            return json.dumps(
                {
                    "errorCode": 400,
                    "message": f"Priority ID must be a valid integer, "
                    f"got: {priority_id}",
                },
                indent=2,
            )

    # Validate status_id if provided
    parsed_status_id = None
    if status_id is not None:
        try:
            parsed_status_id = int(status_id)
            if parsed_status_id <= 0:
                return json.dumps(
                    {
                        "errorCode": 400,
                        "message": f"Status ID must be a positive integer, "
                        f"got: {status_id}",
                    },
                    indent=2,
                )
        except (ValueError, TypeError):
            return json.dumps(
                {
                    "errorCode": 400,
                    "message": f"Status ID must be a valid integer, "
                    f"got: {status_id}",
                },
                indent=2,
            )

    parsed_folder_id = None
    if folder_id is not None:
        try:
            parsed_folder_id = int(folder_id)
            # Use validation utility
            validation = validate_folder_id(parsed_folder_id)
            if not validation.is_valid:
                return json.dumps(
                    {"errorCode": 400, "message": "; ".join(validation.errors)},
                    indent=2,
                )
        except (ValueError, TypeError):
            return json.dumps(
                {
                    "errorCode": 400,
                    "message": f"Folder ID must be a valid integer, got: {folder_id}",
                },
                indent=2,
            )

    # Convert and validate labels
    parsed_labels = None
    if labels is not None:
        try:
            # Try JSON array format first
            parsed_labels = json.loads(labels)
            if not isinstance(parsed_labels, list):
                return json.dumps(
                    {
                        "errorCode": 400,
                        "message": "Labels must be a JSON array (e.g., "
                        '\'["automation", "smoke"]\') or comma-separated string',
                    },
                    indent=2,
                )
            # Validate all items are strings
            for item in parsed_labels:
                if not isinstance(item, str):
                    return json.dumps(
                        {"errorCode": 400, "message": "All labels must be strings"},
                        indent=2,
                    )
        except json.JSONDecodeError:
            # Fall back to comma-separated format
            try:
                parsed_labels = [
                    label.strip() for label in labels.split(",") if label.strip()
                ]
                if not parsed_labels:
                    return json.dumps(
                        {
                            "errorCode": 400,
                            "message": "Labels cannot be empty. Use JSON array "
                            "format or comma-separated values",
                        },
                        indent=2,
                    )
            except Exception as e:
                return json.dumps(
                    {
                        "errorCode": 400,
                        "message": f"Failed to parse labels: {str(e)}. Use JSON array "
                        'format (e.g., \'["label1", "label2"]\') or comma-separated '
                        "(e.g., 'label1, label2')",
                    },
                    indent=2,
                )

    # Convert and validate custom fields
    parsed_custom_fields = None
    if custom_fields is not None:
        if isinstance(custom_fields, dict):
            # Already a dictionary (parsed by MCP framework)
            parsed_custom_fields = custom_fields
        elif isinstance(custom_fields, str):
            # String input - parse as JSON
            try:
                parsed_custom_fields = json.loads(custom_fields)
                if not isinstance(parsed_custom_fields, dict):
                    return json.dumps(
                        {
                            "errorCode": 400,
                            "message": "Custom fields must be a JSON object (e.g., "
                            '\'{"Components": ["Update"], "Version": "v1.0.0"}\')',
                        },
                        indent=2,
                    )
            except json.JSONDecodeError as e:
                return json.dumps(
                    {
                        "errorCode": 400,
                        "message": f"Custom fields must be valid JSON: {str(e)}. "
                        'Example: \'{"Components": ["Update"], "Version": "v1.0.0"}\'',
                    },
                    indent=2,
                )
            except Exception as e:
                return json.dumps(
                    {
                        "errorCode": 400,
                        "message": f"Failed to parse custom fields: {str(e)}",
                    },
                    indent=2,
                )
        else:
            return json.dumps(
                {
                    "errorCode": 400,
                    "message": "Custom fields must be a JSON object or JSON string. "
                    'Example: \'{"Components": ["Update"], "Version": "v1.0.0"}\'',
                },
                indent=2,
            )

    # Use provided IDs directly - no lookups needed
    resolved_priority_id = parsed_priority_id if priority_id is not None else None
    resolved_status_id = parsed_status_id if status_id is not None else None
    resolved_folder_id = parsed_folder_id if folder_id is not None else None

    test_case_data = {}

    # Add optional fields only if they are provided
    if name is not None:
        test_case_data["name"] = name

    if objective is not None:
        test_case_data["objective"] = objective

    if precondition is not None:
        test_case_data["precondition"] = precondition

    if parsed_estimated_time is not None:
        test_case_data["estimatedTime"] = parsed_estimated_time

    if parsed_component_id is not None:
        # The API expects a component object with id and self
        test_case_data["component"] = {"id": parsed_component_id}

    # Use resolved priority ID if priority_name was provided
    if resolved_priority_id is not None:
        # The API expects a priority object with id and self
        test_case_data["priority"] = {"id": resolved_priority_id}

    # Use resolved status ID if status_name was provided
    if resolved_status_id is not None:
        # The API expects a status object with id and self
        test_case_data["status"] = {"id": resolved_status_id}

    if resolved_folder_id is not None:
        # Use folderId (which the client will convert to folder object)
        test_case_data["folderId"] = resolved_folder_id

    if owner_id is not None:
        test_case_data["ownerId"] = owner_id

    if parsed_labels is not None:
        test_case_data["labels"] = parsed_labels

    if parsed_custom_fields is not None:
        test_case_data["customFields"] = parsed_custom_fields

    # Validate complete test case update input
    validation_result = validate_test_case_update_input(test_case_data)
    if not validation_result.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(validation_result.errors)},
            indent=2,
        )

    # Update test case via API
    result = await zephyr_client.update_test_case(
        test_case_key=test_case_key, test_case_input=validation_result.data
    )

    if result.is_valid:
        # PUT returns 200 with no content according to API spec
        return json.dumps(
            {
                "message": f"Test case '{test_case_key}' updated successfully",
                "testCaseKey": test_case_key,
            },
            indent=2,
        )
    else:
        return json.dumps(
            {
                "errorCode": 400,
                "message": (
                    "; ".join(result.errors)
                    if result.errors
                    else f"Failed to update test case {test_case_key}"
                ),
            },
            indent=2,
        )


# ============================================================================
# Test Cycle Management Tools
# ============================================================================


@mcp.tool()
async def get_test_cycles(
    project_key: str | None = None,
    folder_id: str | None = None,
    jira_project_version_id: str | None = None,
    max_results: int = 10,
    start_at: int = 0,
) -> str:
    """Get test cycles using traditional offset-based pagination.

    This tool uses the stable /testcycles endpoint that provides reliable
    offset-based pagination for retrieving test cycles.

    📖 OFFSET-BASED PAGINATION GUIDE:
    Offset pagination works like pages in a book - you specify which "page" to start
    reading from and how many items per "page".

    🔢 HOW TO PAGINATE THROUGH ALL RESULTS:
    1. FIRST REQUEST: start_at=0, max_results=1000 (gets items 0-999)
    2. NEXT REQUEST: start_at=1000, max_results=1000 (gets items 1000-1999)
    3. CONTINUE: start_at=2000, max_results=1000 (gets items 2000-2999)
    4. STOP when response has fewer items than max_results

    💡 PAGINATION FORMULA:
    - Next start_at = current_start_at + max_results
    - Example: If start_at=0 and max_results=1000, next start_at=1000
    - Always ensure start_at is a multiple of max_results (as per API docs)

    ⚡ PERFORMANCE TIP:
    Use max_results=1000 (maximum allowed) for fastest data retrieval.
    The API default is only 10, which is very slow for large datasets.

    🛑 IMPORTANT:
    - start_at should be a multiple of max_results (API requirement)
    - Check response length vs max_results to detect the last page
    - Server may return fewer results than requested due to constraints

    Args:
        project_key: Jira project key filter (e.g., 'PROJ'). If you have access to
                    more than 1000 projects, this parameter may be mandatory.
                    Uses ZEPHYR_SCALE_DEFAULT_PROJECT_KEY if not provided
        folder_id: ID of a folder to filter test cycles (optional)
        jira_project_version_id: Jira project version ID to filter test cycles
                                 (optional)
        max_results: Maximum number of results to return (default: 10, max: 1000).
                    RECOMMENDATION: Use 1000 for fastest bulk data retrieval.
        start_at: Zero-indexed starting position (default: 0).
                 MUST be a multiple of max_results.
                 For next page: start_at + max_results

    Returns:
        JSON response with test cycles and pagination information.
        Check if len(values) < max_results to detect the last page.
    """
    if not zephyr_client:
        return _CONFIG_ERROR_MSG

    # Get project key with default fallback
    project_key = get_project_key_with_default(project_key)

    # Parse optional folder_id
    parsed_folder_id = None
    if folder_id is not None:
        try:
            folder_id_int = int(folder_id)
            folder_validation = validate_folder_id(folder_id_int)
            if not folder_validation.is_valid:
                return json.dumps(
                    {"errorCode": 400, "message": "; ".join(folder_validation.errors)},
                    indent=2,
                )
            parsed_folder_id = folder_validation.data
        except (ValueError, TypeError):
            return json.dumps(
                {
                    "errorCode": 400,
                    "message": f"Folder ID must be a valid integer, got: {folder_id}",
                },
                indent=2,
            )

    # Parse optional jira_project_version_id
    parsed_version_id = None
    if jira_project_version_id is not None:
        version_validation = validate_jira_version_id(jira_project_version_id)
        if not version_validation.is_valid:
            return json.dumps(
                {"errorCode": 400, "message": "; ".join(version_validation.errors)},
                indent=2,
            )
        parsed_version_id = version_validation.data

    # Get test cycles from API
    result = await zephyr_client.get_test_cycles(
        project_key=project_key,
        folder_id=parsed_folder_id,
        jira_project_version_id=parsed_version_id,
        max_results=max_results,
        start_at=start_at,
    )

    if result.is_valid:
        return json.dumps(
            result.data.model_dump(by_alias=True, exclude_none=True), indent=2
        )
    else:
        return json.dumps(
            {
                "errorCode": 400,
                "message": (
                    "; ".join(result.errors)
                    if result.errors
                    else "Failed to retrieve test cycles"
                ),
            },
            indent=2,
        )


@mcp.tool()
async def get_test_cycle(test_cycle_key: str) -> str:
    """Get detailed information for a specific test cycle in Zephyr Scale Cloud.

    Args:
        test_cycle_key: The key of the test cycle (format: [PROJECT]-R[NUMBER])

    Returns:
        Formatted test cycle information or error message
    """
    if not zephyr_client:
        return _CONFIG_ERROR_MSG

    # Validate test cycle key
    test_cycle_validation = validate_test_cycle_key(test_cycle_key)
    if not test_cycle_validation.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(test_cycle_validation.errors)},
            indent=2,
        )

    # Get test cycle from API
    result = await zephyr_client.get_test_cycle(test_cycle_key=test_cycle_key)

    if result.is_valid:
        return json.dumps(
            result.data.model_dump(by_alias=True, exclude_none=True), indent=2
        )
    else:
        return json.dumps(
            {
                "errorCode": 404,
                "message": (
                    f"Test cycle '{test_cycle_key}' does not exist or you do not "
                    "have access to it"
                ),
            },
            indent=2,
        )


@mcp.tool()
async def create_test_cycle(
    name: str,
    project_key: str | None = None,
    description: str | None = None,
    planned_start_date: str | None = None,
    planned_end_date: str | None = None,
    jira_project_version: str | None = None,
    status_name: str | None = None,
    folder_id: str | None = None,
    owner_id: str | None = None,
    custom_fields: str | dict | None = None,
) -> str:
    """Create a new test cycle in Zephyr Scale Cloud.

    Args:
        name: Test cycle name
        project_key: Jira project key (optional, uses
                     ZEPHYR_SCALE_DEFAULT_PROJECT_KEY if not provided)
        description: Test cycle description (optional)
        planned_start_date: Planned start date
                            (format: yyyy-MM-dd'T'HH:mm:ss'Z',
                            e.g., 2018-05-19T13:15:13Z) (optional)
        planned_end_date: Planned end date
                          (format: yyyy-MM-dd'T'HH:mm:ss'Z',
                          e.g., 2018-05-20T13:15:13Z) (optional)
        jira_project_version: Jira project version ID as string (optional)
        status_name: Status name, defaults to default status if not specified (optional)
        folder_id: Folder ID as string to place the test cycle (optional)
        owner_id: Jira user account ID for owner (optional)
        custom_fields: Custom fields as JSON string or dict (e.g.,
                      '{"Environment": "Production", "Release": "v1.0.0"}' or
                      {"Environment": "Production", "Release": "v1.0.0"}) (optional)

    Returns:
        Success message with created test cycle details or error message
    """
    if not zephyr_client:
        return _CONFIG_ERROR_MSG

    # Get project key with default fallback
    project_key = get_project_key_with_default(project_key)

    # Validate project key (required for CREATE operations)
    project_validation = validate_project_key(project_key)
    if not project_validation.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(project_validation.errors)},
            indent=2,
        )

    # Validate name
    if not name or not name.strip():
        return json.dumps(
            {"errorCode": 400, "message": "Test cycle name is required"},
            indent=2,
        )

    # Parse optional folder_id
    parsed_folder_id = None
    if folder_id is not None:
        try:
            parsed_folder_id = int(folder_id)
            folder_validation = validate_folder_id(parsed_folder_id)
            if not folder_validation.is_valid:
                return json.dumps(
                    {"errorCode": 400, "message": "; ".join(folder_validation.errors)},
                    indent=2,
                )
        except (ValueError, TypeError):
            return json.dumps(
                {
                    "errorCode": 400,
                    "message": f"Folder ID must be a valid integer, got: {folder_id}",
                },
                indent=2,
            )

    # Parse optional jira_project_version
    parsed_version_id = None
    if jira_project_version is not None:
        version_validation = validate_jira_version_id(jira_project_version)
        if not version_validation.is_valid:
            return json.dumps(
                {"errorCode": 400, "message": "; ".join(version_validation.errors)},
                indent=2,
            )
        parsed_version_id = version_validation.data

    # Parse custom_fields if provided
    parsed_custom_fields = None
    if custom_fields is not None:
        if isinstance(custom_fields, str):
            try:
                parsed_custom_fields = json.loads(custom_fields)
            except json.JSONDecodeError:
                return json.dumps(
                    {
                        "errorCode": 400,
                        "message": "Invalid JSON format for custom_fields parameter",
                    },
                    indent=2,
                )
        elif isinstance(custom_fields, dict):
            parsed_custom_fields = custom_fields
        else:
            return json.dumps(
                {
                    "errorCode": 400,
                    "message": "custom_fields must be a JSON string or dict",
                },
                indent=2,
            )

    # Build test cycle data
    test_cycle_data = {
        "projectKey": project_key,
        "name": name,
    }

    # Add optional fields
    if description is not None:
        test_cycle_data["description"] = description

    if planned_start_date is not None:
        test_cycle_data["plannedStartDate"] = planned_start_date

    if planned_end_date is not None:
        test_cycle_data["plannedEndDate"] = planned_end_date

    if parsed_version_id is not None:
        test_cycle_data["jiraProjectVersion"] = parsed_version_id

    if status_name is not None:
        test_cycle_data["statusName"] = status_name

    if parsed_folder_id is not None:
        test_cycle_data["folderId"] = parsed_folder_id

    if owner_id is not None:
        test_cycle_data["ownerId"] = owner_id

    if parsed_custom_fields is not None:
        test_cycle_data["customFields"] = parsed_custom_fields

    # Validate complete test cycle input
    validation_result = validate_test_cycle_input(test_cycle_data)
    if not validation_result.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(validation_result.errors)},
            indent=2,
        )

    # Create test cycle via API
    result = await zephyr_client.create_test_cycle(
        test_cycle_input=validation_result.data
    )

    if result.is_valid:
        return json.dumps(
            result.data.model_dump(by_alias=True, exclude_none=True), indent=2
        )
    else:
        return json.dumps(
            {
                "errorCode": 400,
                "message": (
                    "; ".join(result.errors)
                    if result.errors
                    else f"Failed to create test cycle in project {project_key}"
                ),
            },
            indent=2,
        )


@mcp.tool()
async def update_test_cycle(
    test_cycle_key: str,
    name: str | None = None,
    description: str | None = None,
    planned_start_date: str | None = None,
    planned_end_date: str | None = None,
    jira_project_version_id: str | None = None,
    status_id: str | None = None,
    folder_id: str | None = None,
    owner_id: str | None = None,
    custom_fields: str | dict | None = None,
) -> str:
    """Update an existing test cycle in Zephyr Scale Cloud.

    Args:
        test_cycle_key: The key of the test cycle to update
                        (format: [PROJECT]-R[NUMBER])
        name: Test cycle name (optional)
        description: Test cycle description (optional)
        planned_start_date: Planned start date
                            (format: yyyy-MM-dd'T'HH:mm:ss'Z') (optional)
        planned_end_date: Planned end date (format: yyyy-MM-dd'T'HH:mm:ss'Z') (optional)
        jira_project_version_id: Jira project version ID as string (optional)
        status_id: Status ID as string (optional, use get_statuses to find IDs)
        folder_id: Folder ID as string (optional, use get_folders to find IDs)
        owner_id: Jira user account ID for owner (optional)
        custom_fields: Custom fields as JSON string or dict (e.g.,
                      '{"Environment": "Production"}' or
                      {"Environment": "Production"}) (optional)

    Returns:
        Success message or error message
    """
    if not zephyr_client:
        return _CONFIG_ERROR_MSG

    # Validate test cycle key
    test_cycle_validation = validate_test_cycle_key(test_cycle_key)
    if not test_cycle_validation.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(test_cycle_validation.errors)},
            indent=2,
        )

    # First, get the existing test cycle
    get_result = await zephyr_client.get_test_cycle(test_cycle_key=test_cycle_key)
    if not get_result.is_valid:
        return json.dumps(
            {
                "errorCode": 404,
                "message": (
                    f"Test cycle '{test_cycle_key}' does not exist or you do not "
                    "have access to it"
                ),
            },
            indent=2,
        )

    # Get the existing test cycle data
    test_cycle = get_result.data

    # Update fields if provided
    if name is not None:
        test_cycle.name = name

    if description is not None:
        test_cycle.description = description

    if planned_start_date is not None:
        test_cycle.planned_start_date = planned_start_date

    if planned_end_date is not None:
        test_cycle.planned_end_date = planned_end_date

    if jira_project_version_id is not None:
        version_validation = validate_jira_version_id(jira_project_version_id)
        if not version_validation.is_valid:
            return json.dumps(
                {"errorCode": 400, "message": "; ".join(version_validation.errors)},
                indent=2,
            )
        from ..schemas.test_cycle import JiraProjectVersion

        test_cycle.jira_project_version = JiraProjectVersion(id=version_validation.data)

    if status_id is not None:
        status_id_int = int(status_id)

        # We need to preserve the status structure
        if test_cycle.status:
            test_cycle.status.id = status_id_int

    if folder_id is not None:
        try:
            folder_id_int = int(folder_id)
            folder_validation = validate_folder_id(folder_id_int)
            if not folder_validation.is_valid:
                return json.dumps(
                    {"errorCode": 400, "message": "; ".join(folder_validation.errors)},
                    indent=2,
                )
            from ..schemas.folder import FolderLink

            test_cycle.folder = FolderLink(id=folder_validation.data)
        except (ValueError, TypeError):
            return json.dumps(
                {
                    "errorCode": 400,
                    "message": f"Folder ID must be a valid integer, got: {folder_id}",
                },
                indent=2,
            )

    if owner_id is not None:
        from ..schemas.test_cycle import JiraUserLink

        test_cycle.owner = JiraUserLink(account_id=owner_id)

    if custom_fields is not None:
        if isinstance(custom_fields, str):
            try:
                parsed_custom_fields = json.loads(custom_fields)
            except json.JSONDecodeError:
                return json.dumps(
                    {
                        "errorCode": 400,
                        "message": "Invalid JSON format for custom_fields parameter",
                    },
                    indent=2,
                )
        elif isinstance(custom_fields, dict):
            parsed_custom_fields = custom_fields
        else:
            return json.dumps(
                {
                    "errorCode": 400,
                    "message": "custom_fields must be a JSON string or dict",
                },
                indent=2,
            )
        from ..schemas.common import CustomFields

        test_cycle.custom_fields = CustomFields(**parsed_custom_fields)

    # Update test cycle via API
    result = await zephyr_client.update_test_cycle(
        test_cycle_key=test_cycle_key, test_cycle=test_cycle
    )

    if result.is_valid:
        return json.dumps(
            {"message": f"Test cycle {test_cycle_key} updated successfully"}, indent=2
        )
    else:
        return json.dumps(
            {
                "errorCode": 400,
                "message": (
                    "; ".join(result.errors)
                    if result.errors
                    else f"Failed to update test cycle {test_cycle_key}"
                ),
            },
            indent=2,
        )


@mcp.tool()
async def get_test_cycle_links(test_cycle_key: str) -> str:
    """Get all links (issues + web links) for a test cycle in Zephyr Scale Cloud.

    Args:
        test_cycle_key: The key of the test cycle (format: [PROJECT]-R[NUMBER])

    Returns:
        Formatted list of links or error message
    """
    if not zephyr_client:
        return _CONFIG_ERROR_MSG

    # Validate test cycle key
    test_cycle_validation = validate_test_cycle_key(test_cycle_key)
    if not test_cycle_validation.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(test_cycle_validation.errors)},
            indent=2,
        )

    # Get links from API
    result = await zephyr_client.get_test_cycle_links(test_cycle_key=test_cycle_key)

    if result.is_valid:
        return json.dumps(
            result.data.model_dump(by_alias=True, exclude_none=True), indent=2
        )
    else:
        return json.dumps(
            {
                "errorCode": 404,
                "message": (
                    f"Test cycle '{test_cycle_key}' does not exist or you do not "
                    "have access to it"
                ),
            },
            indent=2,
        )


@mcp.tool()
async def create_test_cycle_issue_link(test_cycle_key: str, issue_id: int) -> str:
    """Create a link between a test cycle and a Jira issue in Zephyr Scale Cloud.

    Args:
        test_cycle_key: The key of the test cycle (format: [PROJECT]-R[NUMBER])
        issue_id: The numeric Jira issue ID to link to (NOT the issue key)
                  Use the Atlassian/Jira MCP tool to get the issue ID from a key

    Returns:
        Success message with created link ID or error message
    """
    if not zephyr_client:
        return _CONFIG_ERROR_MSG

    # Validate test cycle key
    test_cycle_validation = validate_test_cycle_key(test_cycle_key)
    if not test_cycle_validation.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(test_cycle_validation.errors)},
            indent=2,
        )

    # Validate issue_id
    issue_validation = validate_issue_id(issue_id)
    if not issue_validation.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(issue_validation.errors)}, indent=2
        )

    # Prepare link input
    link_data = {"issueId": issue_validation.data}
    link_validation = validate_issue_link_input(link_data)
    if not link_validation.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(link_validation.errors)}, indent=2
        )

    # Create link via API
    result = await zephyr_client.create_test_cycle_issue_link(
        test_cycle_key=test_cycle_key, issue_link_input=link_validation.data
    )

    if result.is_valid:
        return json.dumps(
            result.data.model_dump(by_alias=True, exclude_none=True), indent=2
        )
    else:
        return json.dumps(
            {
                "errorCode": 400,
                "message": (
                    "; ".join(result.errors)
                    if result.errors
                    else f"Failed to create issue link for test cycle {test_cycle_key}"
                ),
            },
            indent=2,
        )


@mcp.tool()
async def create_test_cycle_web_link(
    test_cycle_key: str, url: str, description: str | None = None
) -> str:
    """Create a link between a test cycle and a web URL in Zephyr Scale Cloud.

    Args:
        test_cycle_key: The key of the test cycle (format: [PROJECT]-R[NUMBER])
        url: The web URL to link to
        description: Optional description for the link

    Returns:
        Success message with created link ID or error message
    """
    if not zephyr_client:
        return _CONFIG_ERROR_MSG

    # Validate test cycle key
    test_cycle_validation = validate_test_cycle_key(test_cycle_key)
    if not test_cycle_validation.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(test_cycle_validation.errors)},
            indent=2,
        )

    # Prepare link input
    link_data = {"url": url}
    if description is not None:
        link_data["description"] = description

    link_validation = validate_web_link_input(link_data)
    if not link_validation.is_valid:
        return json.dumps(
            {"errorCode": 400, "message": "; ".join(link_validation.errors)}, indent=2
        )

    # Create link via API
    result = await zephyr_client.create_test_cycle_web_link(
        test_cycle_key=test_cycle_key, web_link_input=link_validation.data
    )

    if result.is_valid:
        return json.dumps(
            result.data.model_dump(by_alias=True, exclude_none=True), indent=2
        )
    else:
        return json.dumps(
            {
                "errorCode": 400,
                "message": (
                    "; ".join(result.errors)
                    if result.errors
                    else f"Failed to create web link for test cycle {test_cycle_key}"
                ),
            },
            indent=2,
        )


def main():
    """Run the MCP server.

    This starts the MCP server that AI assistants can connect to.
    """
    mcp.run()


if __name__ == "__main__":
    main()
