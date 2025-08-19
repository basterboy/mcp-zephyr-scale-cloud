"""MCP Server for Zephyr Scale Cloud.

This file contains the Model Context Protocol (MCP) SERVER implementation.
The MCP server exposes tools, resources, and prompts that AI assistants can use
to interact with Zephyr Scale Cloud.

Architecture:
- MCP Server (this file): Handles MCP protocol, exposes tools to AI assistants
- HTTP Client (clients/): Makes REST API calls to Zephyr Scale Cloud
- AI Assistant: Connects to MCP server to access Zephyr Scale functionality
"""

from dotenv import load_dotenv
from mcp.server import FastMCP

from .clients.zephyr_client import ZephyrClient
from .config import ZephyrConfig

# Load environment variables
load_dotenv()

# Initialize MCP server - this is the MCP SERVER
mcp = FastMCP("Zephyr Scale Cloud")

# Error message constants for reuse
_CONFIG_ERROR_MSG = (
    "❌ ERROR: Zephyr Scale configuration not found. "
    "Please set ZEPHYR_SCALE_API_TOKEN environment variable."
)

_ERROR_DETAILS_FORMAT = "❌ ERROR: {error}\n🔍 Details: {details}"

# Initialize HTTP client for Zephyr Scale API
try:
    config = ZephyrConfig.from_env()
    zephyr_client = ZephyrClient(config)  # This is an HTTP CLIENT
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

    try:
        # Use the HTTP client to check Zephyr Scale API
        health_data = await zephyr_client.healthcheck()

        if health_data.get("status") == "UP":
            return (
                f"✅ SUCCESS: Zephyr Scale Cloud API is healthy\n"
                f"📍 Base URL: {config.base_url}\n"
                f"🔑 Authentication: Valid\n"
                f"📊 Status: {health_data.get('status', 'Unknown')}"
            )
        else:
            error_msg = health_data.get("error", "Unknown error")
            return (
                f"❌ ERROR: Zephyr Scale Cloud API health check failed\n"
                f"📍 Base URL: {config.base_url}\n"
                f"🔍 Error: {error_msg}"
            )

    except Exception as e:
        return (
            f"❌ EXCEPTION: Failed to perform health check\n"
            f"📍 Base URL: {config.base_url if config else 'Not configured'}\n"
            f"🔍 Error: {str(e)}"
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

    try:
        result = await zephyr_client.get_priorities(
            project_key=project_key, max_results=max_results
        )

        if "error" in result:
            return _ERROR_DETAILS_FORMAT.format(
                error=result["error"], details=result.get("message", "Unknown error")
            )

        priorities = result.get("values", [])
        total = result.get("total", len(priorities))

        if not priorities:
            filter_msg = f" for project {project_key}" if project_key else ""
            return f"📋 No priorities found{filter_msg}."

        output = f"📋 **Priorities** ({len(priorities)} of {total})\n"
        if project_key:
            output += f"🏷️ Project: {project_key}\n"
        output += "\n"

        for priority in priorities:
            output += (
                f"**{priority.get('name', 'Unknown')}** (ID: {priority.get('id')})\n"
            )
            if priority.get("description"):
                output += f"   📝 {priority['description']}\n"
            output += f"   📊 Index: {priority.get('index', 'N/A')}"
            if priority.get("default"):
                output += " ⭐ (Default)"
            if priority.get("color"):
                output += f" 🎨 {priority['color']}"
            project_id = priority.get("project", {}).get("id", "Unknown")
            output += f"\n   🏗️ Project: {project_id}\n\n"

        return output.strip()

    except Exception as e:
        return f"❌ EXCEPTION: Failed to retrieve priorities\n🔍 Error: {str(e)}"


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

    try:
        result = await zephyr_client.get_priority(priority_id)

        if "error" in result:
            return _ERROR_DETAILS_FORMAT.format(
                error=result["error"], details=result.get("message", "Unknown error")
            )

        output = "📋 **Priority Details**\n\n"
        output += f"**{result.get('name', 'Unknown')}** (ID: {result.get('id')})\n"

        if result.get("description"):
            output += f"📝 **Description:** {result['description']}\n"

        output += f"📊 **Index:** {result.get('index', 'N/A')}\n"

        if result.get("default"):
            output += "⭐ **Default Priority:** Yes\n"

        if result.get("color"):
            output += f"🎨 **Color:** {result['color']}\n"

        project = result.get("project", {})
        if project:
            output += f"🏗️ **Project:** {project.get('id', 'Unknown')}\n"

        return output

    except Exception as e:
        return (
            f"❌ EXCEPTION: Failed to retrieve priority {priority_id}\n"
            f"🔍 Error: {str(e)}"
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

    # Validate inputs
    if not name or len(name.strip()) == 0:
        return "❌ ERROR: Priority name is required and cannot be empty."

    if len(name) > 255:
        return "❌ ERROR: Priority name cannot exceed 255 characters."

    if description and len(description) > 255:
        return "❌ ERROR: Priority description cannot exceed 255 characters."

    if color and not color.startswith("#"):
        return "❌ ERROR: Color must be in hex format (e.g., '#FF0000')."

    try:
        result = await zephyr_client.create_priority(
            project_key=project_key,
            name=name.strip(),
            description=description.strip() if description else None,
            color=color,
        )

        if "error" in result:
            return _ERROR_DETAILS_FORMAT.format(
                error=result["error"], details=result.get("message", "Unknown error")
            )

        priority_id = result.get("id")
        output = "✅ **Priority Created Successfully!**\n\n"
        output += f"🆔 **ID:** {priority_id}\n"
        output += f"📋 **Name:** {name}\n"
        output += f"🏷️ **Project:** {project_key}\n"

        if description:
            output += f"📝 **Description:** {description}\n"

        if color:
            output += f"🎨 **Color:** {color}\n"

        if result.get("self"):
            output += f"🔗 **URL:** {result['self']}\n"

        return output

    except Exception as e:
        return f"❌ EXCEPTION: Failed to create priority\n🔍 Error: {str(e)}"


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

    # Validate inputs
    if not name or len(name.strip()) == 0:
        return "❌ ERROR: Priority name is required and cannot be empty."

    if len(name) > 255:
        return "❌ ERROR: Priority name cannot exceed 255 characters."

    if description and len(description) > 255:
        return "❌ ERROR: Priority description cannot exceed 255 characters."

    if color and not color.startswith("#"):
        return "❌ ERROR: Color must be in hex format (e.g., '#FF0000')."

    if index < 0:
        return "❌ ERROR: Index must be a non-negative integer."

    try:
        result = await zephyr_client.update_priority(
            priority_id=priority_id,
            project_id=project_id,
            name=name.strip(),
            index=index,
            default=default,
            description=description.strip() if description else None,
            color=color,
        )

        if "error" in result:
            return _ERROR_DETAILS_FORMAT.format(
                error=result["error"], details=result.get("message", "Unknown error")
            )

        output = "✅ **Priority Updated Successfully!**\n\n"
        output += f"🆔 **ID:** {priority_id}\n"
        output += f"📋 **Name:** {name}\n"
        output += f"🏗️ **Project ID:** {project_id}\n"
        output += f"📊 **Index:** {index}\n"

        if default:
            output += "⭐ **Default Priority:** Yes\n"

        if description:
            output += f"📝 **Description:** {description}\n"

        if color:
            output += f"🎨 **Color:** {color}\n"

        return output

    except Exception as e:
        return (
            f"❌ EXCEPTION: Failed to update priority {priority_id}\n🔍 Error: {str(e)}"
        )


def main():
    """Run the MCP server.

    This starts the MCP server that AI assistants can connect to.
    """
    mcp.run()


if __name__ == "__main__":
    main()
