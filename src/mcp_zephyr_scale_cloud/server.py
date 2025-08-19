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

# Initialize HTTP client for Zephyr Scale API
try:
    config = ZephyrConfig.from_env()
    zephyr_client = ZephyrClient(config)  # This is an HTTP CLIENT
except ValueError as e:
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
        str: Health status information including API connectivity and authentication status.
    """
    if not zephyr_client:
        return "❌ ERROR: Zephyr Scale configuration not found. Please set ZEPHYR_SCALE_API_TOKEN environment variable."
    
    try:
        # Use the HTTP client to check Zephyr Scale API
        health_data = await zephyr_client.healthcheck()
        
        if health_data.get("status") == "UP":
            return f"✅ SUCCESS: Zephyr Scale Cloud API is healthy\n" \
                   f"📍 Base URL: {config.base_url}\n" \
                   f"🔑 Authentication: Valid\n" \
                   f"📊 Status: {health_data.get('status', 'Unknown')}"
        else:
            error_msg = health_data.get('error', 'Unknown error')
            return f"❌ ERROR: Zephyr Scale Cloud API health check failed\n" \
                   f"📍 Base URL: {config.base_url}\n" \
                   f"🔍 Error: {error_msg}"
                   
    except Exception as e:
        return f"❌ EXCEPTION: Failed to perform health check\n" \
               f"📍 Base URL: {config.base_url if config else 'Not configured'}\n" \
               f"🔍 Error: {str(e)}"


def main():
    """Run the MCP server.
    
    This starts the MCP server that AI assistants can connect to.
    """
    mcp.run()


if __name__ == "__main__":
    main()