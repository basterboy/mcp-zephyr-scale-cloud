"""Pytest configuration and shared fixtures."""

import asyncio
import os
from collections.abc import Generator
from unittest.mock import AsyncMock

import httpx
import pytest
from pydantic import ValidationError

from src.mcp_zephyr_scale_cloud.clients.zephyr_client import ZephyrClient
from src.mcp_zephyr_scale_cloud.config import ZephyrConfig


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_env_vars() -> Generator[dict[str, str], None, None]:
    """Mock environment variables for testing."""
    original_env = os.environ.copy()
    test_env = {
        "ZEPHYR_SCALE_API_TOKEN": "test_token_123",
        "ZEPHYR_SCALE_BASE_URL": "https://api.example.com/v2",
        "ZEPHYR_SCALE_DEFAULT_PROJECT_KEY": "TEST",
    }

    os.environ.update(test_env)
    yield test_env

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_config(mock_env_vars) -> ZephyrConfig:
    """Create a mock ZephyrConfig for testing."""
    return ZephyrConfig.from_env()


@pytest.fixture
def sample_priority_data() -> dict:
    """Sample priority data for testing."""
    return {
        "id": 1,
        "name": "High",
        "description": "High priority test item",
        "index": 0,
        "default": False,
        "color": "#FF0000",
        "project": {
            "id": 123,
            "key": "TEST",
            "name": "Test Project",
            "self": "https://api.example.com/v2/projects/123",
        },
        "self": "https://api.example.com/v2/priorities/1",
    }


@pytest.fixture
def sample_priority_list() -> dict:
    """Sample priority list response for testing."""
    return {
        "values": [
            {
                "id": 1,
                "name": "Low",
                "description": "Low priority",
                "index": 0,
                "default": False,
                "color": "#00FF00",
                "project": {
                    "id": 123,
                    "key": "TEST",
                    "self": "https://api.example.com/v2/projects/123",
                },
                "self": "https://api.example.com/v2/priorities/1",
            },
            {
                "id": 2,
                "name": "High",
                "description": "High priority",
                "index": 1,
                "default": True,
                "color": "#FF0000",
                "project": {
                    "id": 123,
                    "key": "TEST",
                    "self": "https://api.example.com/v2/projects/123",
                },
                "self": "https://api.example.com/v2/priorities/2",
            },
        ],
        "total": 2,
        "maxResults": 50,
        "startAt": 0,
        "isLast": True,
    }


@pytest.fixture
def mock_httpx_client() -> AsyncMock:
    """Mock httpx.AsyncClient for testing."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    return mock_client


@pytest.fixture
async def mock_zephyr_client(mock_config: ZephyrConfig) -> ZephyrClient:
    """Create a ZephyrClient instance for testing."""
    return ZephyrClient(mock_config)


@pytest.fixture
def sample_created_resource() -> dict:
    """Sample created resource response."""
    return {
        "id": 123,
        "key": "CREATED-123",
        "self": "https://api.example.com/v2/resource/123",
    }


@pytest.fixture
def sample_validation_error() -> ValidationError:
    """Sample Pydantic validation error for testing."""
    try:
        from src.mcp_zephyr_scale_cloud.schemas.priority import CreatePriorityRequest

        CreatePriorityRequest(projectKey="", name="")  # Invalid data
    except ValidationError as e:
        return e

    # Fallback if no error is raised
    from pydantic import BaseModel, Field

    class TestModel(BaseModel):
        required_field: str = Field(..., min_length=1)

    try:
        TestModel(required_field="")
    except ValidationError as e:
        return e
