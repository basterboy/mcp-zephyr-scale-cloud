"""HTTP client for Zephyr Scale Cloud API."""

from typing import Any

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
            "Accept": "application/json",
        }

    async def healthcheck(self) -> dict:
        """Check if Zephyr Scale API is accessible."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.config.base_url}/healthcheck",
                    headers=self.headers,
                    timeout=10.0,
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
                    "message": "Failed to connect to Zephyr Scale Cloud API",
                }

    async def get_priorities(
        self, project_key: str | None = None, max_results: int = 50, start_at: int = 0
    ) -> dict[str, Any]:
        """Get all priorities from Zephyr Scale Cloud.

        Args:
            project_key: Optional Jira project key to filter priorities
            max_results: Maximum number of results to return (default: 50, max: 1000)
            start_at: Zero-indexed starting position (default: 0)

        Returns:
            Dict containing list of priorities and pagination info
        """
        async with httpx.AsyncClient() as client:
            try:
                params = {"maxResults": min(max_results, 1000), "startAt": start_at}
                if project_key:
                    params["projectKey"] = project_key

                response = await client.get(
                    f"{self.config.base_url}/priorities",
                    headers=self.headers,
                    params=params,
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json()

            except httpx.HTTPError as e:
                return {
                    "error": str(e),
                    "message": "Failed to retrieve priorities from Zephyr Scale "
                    "Cloud API",
                }

    async def get_priority(self, priority_id: int) -> dict[str, Any]:
        """Get a specific priority by ID.

        Args:
            priority_id: The ID of the priority to retrieve

        Returns:
            Dict containing priority details
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.config.base_url}/priorities/{priority_id}",
                    headers=self.headers,
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json()

            except httpx.HTTPError as e:
                if hasattr(e, "response") and e.response.status_code == 404:
                    return {
                        "error": "Priority not found",
                        "message": f"Priority with ID {priority_id} does not exist "
                        f"or you do not have access to it",
                    }
                return {
                    "error": str(e),
                    "message": f"Failed to retrieve priority {priority_id} "
                    f"from Zephyr Scale Cloud API",
                }

    async def create_priority(
        self,
        project_key: str,
        name: str,
        description: str | None = None,
        color: str | None = None,
    ) -> dict[str, Any]:
        """Create a new priority.

        Args:
            project_key: Jira project key where the priority will be created
            name: Name of the priority (max 255 characters)
            description: Optional description of the priority (max 255 characters)
            color: Optional color code for the priority (e.g., '#FF0000')

        Returns:
            Dict containing created priority details
        """
        async with httpx.AsyncClient() as client:
            try:
                payload = {"projectKey": project_key, "name": name}
                if description:
                    payload["description"] = description
                if color:
                    payload["color"] = color

                response = await client.post(
                    f"{self.config.base_url}/priorities",
                    headers=self.headers,
                    json=payload,
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json()

            except httpx.HTTPError as e:
                return {
                    "error": str(e),
                    "message": "Failed to create priority in Zephyr Scale Cloud API",
                }

    async def update_priority(
        self,
        priority_id: int,
        project_id: int,
        name: str,
        index: int,
        default: bool = False,
        description: str | None = None,
        color: str | None = None,
    ) -> dict[str, Any]:
        """Update an existing priority.

        Args:
            priority_id: ID of the priority to update
            project_id: ID of the project the priority belongs to
            name: Updated name of the priority
            index: Index/order of the priority
            default: Whether this is the default priority
            description: Optional updated description
            color: Optional updated color code

        Returns:
            Dict containing update result
        """
        async with httpx.AsyncClient() as client:
            try:
                payload = {
                    "id": priority_id,
                    "project": {"id": project_id},
                    "name": name,
                    "index": index,
                    "default": default,
                }
                if description:
                    payload["description"] = description
                if color:
                    payload["color"] = color

                response = await client.put(
                    f"{self.config.base_url}/priorities/{priority_id}",
                    headers=self.headers,
                    json=payload,
                    timeout=10.0,
                )
                response.raise_for_status()

                # Update returns 200 OK with no body
                return {
                    "success": True,
                    "message": f"Priority {priority_id} updated successfully",
                }

            except httpx.HTTPError as e:
                return {
                    "error": str(e),
                    "message": f"Failed to update priority {priority_id} "
                    f"in Zephyr Scale Cloud API",
                }
