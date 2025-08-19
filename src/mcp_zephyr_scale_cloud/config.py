"""Configuration management for Zephyr Scale Cloud MCP server."""

import os

from pydantic import BaseModel, Field


class ZephyrConfig(BaseModel):
    """Configuration for Zephyr Scale Cloud API."""

    api_token: str = Field(..., description="Zephyr Scale API token")
    base_url: str = Field(
        default="https://api.zephyrscale.smartbear.com/v2",
        description="Zephyr Scale API base URL",
    )
    project_key: str | None = Field(
        default=None, description="Default Jira project key"
    )

    @classmethod
    def from_env(cls) -> "ZephyrConfig":
        """Create config from environment variables."""
        api_token = os.getenv("ZEPHYR_SCALE_API_TOKEN")
        if not api_token:
            raise ValueError("ZEPHYR_SCALE_API_TOKEN environment variable is required")

        return cls(
            api_token=api_token,
            base_url=os.getenv(
                "ZEPHYR_SCALE_BASE_URL", "https://api.zephyrscale.smartbear.com/v2"
            ),
            project_key=os.getenv("ZEPHYR_SCALE_DEFAULT_PROJECT_KEY"),
        )
