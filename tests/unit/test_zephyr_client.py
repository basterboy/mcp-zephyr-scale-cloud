"""Tests for ZephyrClient."""

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from src.mcp_zephyr_scale_cloud.clients.zephyr_client import ZephyrClient
from src.mcp_zephyr_scale_cloud.schemas.common import ProjectLink
from src.mcp_zephyr_scale_cloud.schemas.priority import (
    CreatePriorityRequest,
    UpdatePriorityRequest,
)


class TestZephyrClient:
    """Test cases for ZephyrClient."""

    def test_client_initialization(self, mock_config):
        """Test ZephyrClient initialization."""
        client = ZephyrClient(mock_config)

        assert client.config == mock_config
        assert client.headers["Authorization"] == "Bearer test_token_123"
        assert client.headers["Content-Type"] == "application/json"

    @pytest.mark.asyncio
    async def test_healthcheck_success(self, mock_zephyr_client):
        """Test successful healthcheck."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock successful response
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response

            result = await mock_zephyr_client.healthcheck()

            assert result.is_valid
            assert result.data["status"] == "UP"

    @pytest.mark.asyncio
    async def test_healthcheck_failure(self, mock_zephyr_client):
        """Test healthcheck with HTTP error."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock HTTP error
            mock_client.get.side_effect = httpx.ConnectError("Connection failed")

            result = await mock_zephyr_client.healthcheck()

            assert not result.is_valid
            assert "Failed to connect" in result.errors[0]

    @pytest.mark.asyncio
    async def test_get_priorities_success(
        self, mock_zephyr_client, sample_priority_list
    ):
        """Test successful get_priorities."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock successful response
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_priority_list
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response

            result = await mock_zephyr_client.get_priorities()

            assert result.is_valid
            assert len(result.data.values) == 2

    @pytest.mark.asyncio
    async def test_get_priorities_with_project_key(
        self, mock_zephyr_client, sample_priority_list
    ):
        """Test get_priorities with project_key filter."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_priority_list
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response

            result = await mock_zephyr_client.get_priorities(
                project_key="TEST", max_results=10
            )

            assert result.is_valid
            # Verify the correct parameters were passed
            mock_client.get.assert_called_once()
            call_args = mock_client.get.call_args
            assert "params" in call_args.kwargs
            assert call_args.kwargs["params"]["projectKey"] == "TEST"
            assert call_args.kwargs["params"]["maxResults"] == 10

    @pytest.mark.asyncio
    async def test_get_priority_success(self, mock_zephyr_client, sample_priority_data):
        """Test successful get_priority."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_priority_data
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response

            result = await mock_zephyr_client.get_priority(1)

            assert result.is_valid
            assert result.data.id == 1
            assert result.data.name == "High"

    @pytest.mark.asyncio
    async def test_get_priority_not_found(self, mock_zephyr_client):
        """Test get_priority with 404 error."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock 404 error
            mock_error = httpx.HTTPStatusError(
                "Not found", request=AsyncMock(), response=AsyncMock()
            )
            mock_error.response.status_code = 404
            mock_client.get.side_effect = mock_error

            result = await mock_zephyr_client.get_priority(999)

            assert not result.is_valid
            assert "does not exist" in result.errors[0]

    @pytest.mark.asyncio
    async def test_get_priority_invalid_id(self, mock_zephyr_client):
        """Test get_priority with invalid ID."""
        result = await mock_zephyr_client.get_priority(-1)

        assert not result.is_valid
        assert "positive integer" in result.errors[0]

    @pytest.mark.asyncio
    async def test_create_priority_success(
        self, mock_zephyr_client, sample_created_resource
    ):
        """Test successful create_priority."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = AsyncMock()
            mock_response.status_code = 201
            mock_response.json.return_value = sample_created_resource
            mock_response.raise_for_status.return_value = None
            mock_client.post.return_value = mock_response

            request = CreatePriorityRequest(
                projectKey="TEST",
                name="New Priority",
                description="Test priority",
                color="#FF0000",
            )

            result = await mock_zephyr_client.create_priority(request)

            assert result.is_valid
            assert result.data.id == 123

    @pytest.mark.asyncio
    async def test_update_priority_success(self, mock_zephyr_client):
        """Test successful update_priority."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_client.put.return_value = mock_response

            project = ProjectLink(id=123, self="https://api.example.com/projects/123")
            request = UpdatePriorityRequest(
                id=1, project=project, name="Updated Priority", index=0, default=True
            )

            result = await mock_zephyr_client.update_priority(1, request)

            assert result.is_valid
            assert "updated successfully" in result.data["message"]

    @pytest.mark.asyncio
    async def test_update_priority_invalid_id(self, mock_zephyr_client):
        """Test update_priority with invalid ID."""
        project = ProjectLink(id=123, self="https://api.example.com/projects/123")
        request = UpdatePriorityRequest(
            id=1, project=project, name="Updated Priority", index=0, default=True
        )

        result = await mock_zephyr_client.update_priority(-1, request)

        assert not result.is_valid
        assert "positive integer" in result.errors[0]
