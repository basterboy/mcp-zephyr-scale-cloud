"""HTTP client for Zephyr Scale Cloud API."""

import httpx
from ..config import ZephyrConfig


class ZephyrClient:
    """HTTP client for Zephyr Scale Cloud API.
    
    This is an HTTP client that makes requests to the Zephyr Scale Cloud REST API.
    It's used internally by the MCP server to fetch data and perform operations.
    """
    
    def __init__(self, config: ZephyrConfig):
        self.config = config
        self.headers = {
            "Authorization": f"Bearer {config.api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def healthcheck(self) -> dict:
        """Check if Zephyr Scale API is accessible."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.config.base_url}/healthcheck",
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                
                # Zephyr Scale healthcheck returns 200 OK with empty body
                if response.status_code == 200:
                    return {"status": "UP"}
                else:
                    return {"status": "DOWN", "http_status": response.status_code}
                    
            except httpx.HTTPError as e:
                return {
                    "status": "ERROR", 
                    "error": str(e),
                    "message": "Failed to connect to Zephyr Scale Cloud API"
                }
