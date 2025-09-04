"""Tests for ZephyrClient."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.mcp_zephyr_scale_cloud.clients.zephyr_client import ZephyrClient
from src.mcp_zephyr_scale_cloud.schemas.common import ProjectLink
from src.mcp_zephyr_scale_cloud.schemas.priority import (
    CreatePriorityRequest,
    UpdatePriorityRequest,
)
from src.mcp_zephyr_scale_cloud.schemas.status import (
    CreateStatusRequest,
    StatusType,
    UpdateStatusRequest,
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
            mock_response = MagicMock()
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
            mock_response = MagicMock()
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

            mock_response = MagicMock()
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

            mock_response = MagicMock()
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

            mock_response = MagicMock()
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

            mock_response = MagicMock()
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


class TestZephyrClientStatus:
    """Test cases for ZephyrClient status operations."""

    @pytest.mark.asyncio
    async def test_get_statuses_success(self, mock_zephyr_client, sample_status_list):
        """Test successful get_statuses."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock successful response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_status_list
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response

            result = await mock_zephyr_client.get_statuses()

            assert result.is_valid
            assert len(result.data.values) == 3
            assert result.data.values[0].name == "Pass"

    @pytest.mark.asyncio
    async def test_get_statuses_with_filters(
        self, mock_zephyr_client, sample_status_list
    ):
        """Test get_statuses with project and type filters."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_status_list
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response

            result = await mock_zephyr_client.get_statuses(
                project_key="TEST",
                status_type=StatusType.TEST_EXECUTION,
                max_results=100,
            )

            assert result.is_valid
            # Verify the URL was called with correct parameters
            mock_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_status_success(self, mock_zephyr_client, sample_status_data):
        """Test successful get_status."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_status_data
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response

            result = await mock_zephyr_client.get_status(1)

            assert result.is_valid
            assert result.data.id == 1
            assert result.data.name == "In Progress"

    @pytest.mark.asyncio
    async def test_get_status_not_found(self, mock_zephyr_client):
        """Test get_status with non-existent status."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock 404 response
            mock_response = MagicMock()
            mock_response.status_code = 404
            http_error = httpx.HTTPStatusError(
                "404 Not Found", request=MagicMock(), response=mock_response
            )
            http_error.response = mock_response
            mock_client.get.side_effect = http_error

            result = await mock_zephyr_client.get_status(999)

            assert not result.is_valid
            assert "does not exist" in result.errors[0]

    @pytest.mark.asyncio
    async def test_get_status_invalid_id(self, mock_zephyr_client):
        """Test get_status with invalid ID."""
        result = await mock_zephyr_client.get_status(-1)

        assert not result.is_valid
        assert "positive integer" in result.errors[0]

    @pytest.mark.asyncio
    async def test_create_status_success(
        self, mock_zephyr_client, sample_created_resource
    ):
        """Test successful create_status."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.json.return_value = sample_created_resource
            mock_response.raise_for_status.return_value = None
            mock_client.post.return_value = mock_response

            request = CreateStatusRequest(
                project_key="TEST",
                name="New Status",
                type="TEST_EXECUTION",
                description="Newly created status",
            )

            result = await mock_zephyr_client.create_status(request)

            assert result.is_valid
            assert result.data.id == 123
            assert result.data.key == "CREATED-123"

    @pytest.mark.asyncio
    async def test_update_status_success(self, mock_zephyr_client):
        """Test successful update_status."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_client.put.return_value = mock_response

            request = UpdateStatusRequest(
                id=1,
                project={"id": 123},
                name="Updated Status",
                index=5,
                default=False,
                archived=False,
            )

            result = await mock_zephyr_client.update_status(1, request)

            assert result.is_valid
            assert "updated successfully" in result.data["message"]

    @pytest.mark.asyncio
    async def test_update_status_invalid_id(self, mock_zephyr_client):
        """Test update_status with invalid ID."""
        request = UpdateStatusRequest(
            id=1,
            project={"id": 123},
            name="Updated Status",
            index=5,
            default=False,
            archived=False,
        )

        result = await mock_zephyr_client.update_status(-1, request)

        assert not result.is_valid
        assert "positive integer" in result.errors[0]


class TestZephyrClientFolder:
    """Test cases for ZephyrClient folder operations."""

    @pytest.mark.asyncio
    async def test_get_folders_success(self, mock_zephyr_client, sample_folder_list):
        """Test successful get_folders."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = sample_folder_list
            mock_client.get.return_value = mock_response

            result = await mock_zephyr_client.get_folders()

            assert result.is_valid
            assert len(result.data.values) == 3
            assert result.data.values[0].name == "Test Cases"
            assert result.data.values[0].folder_type.value == "TEST_CASE"

    @pytest.mark.asyncio
    async def test_get_folders_with_filters(
        self, mock_zephyr_client, sample_folder_list
    ):
        """Test get_folders with project and folder type filters."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = sample_folder_list
            mock_client.get.return_value = mock_response

            from src.mcp_zephyr_scale_cloud.schemas.folder import FolderType

            result = await mock_zephyr_client.get_folders(
                project_key="TEST", folder_type=FolderType.TEST_CASE, max_results=25
            )

            assert result.is_valid
            mock_client.get.assert_called_once()
            call_args = mock_client.get.call_args
            assert call_args[1]["params"]["projectKey"] == "TEST"
            assert call_args[1]["params"]["folderType"] == "TEST_CASE"
            assert call_args[1]["params"]["maxResults"] == 25

    @pytest.mark.asyncio
    async def test_get_folder_success(self, mock_zephyr_client, sample_folder_data):
        """Test successful get_folder."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = sample_folder_data
            mock_client.get.return_value = mock_response

            result = await mock_zephyr_client.get_folder(1)

            assert result.is_valid
            assert result.data.id == 1
            assert result.data.name == "Test Cases"
            assert result.data.folder_type.value == "TEST_CASE"

    @pytest.mark.asyncio
    async def test_get_folder_not_found(self, mock_zephyr_client):
        """Test get_folder with non-existent folder."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_client.get.side_effect = httpx.HTTPStatusError(
                "Not Found", request=MagicMock(), response=mock_response
            )

            result = await mock_zephyr_client.get_folder(999)

            assert not result.is_valid
            assert "does not exist" in result.errors[0]

    @pytest.mark.asyncio
    async def test_get_folder_invalid_id(self, mock_zephyr_client):
        """Test get_folder with invalid ID."""
        result = await mock_zephyr_client.get_folder(-1)

        assert not result.is_valid
        assert "positive integer" in result.errors[0]

    @pytest.mark.asyncio
    async def test_create_folder_success(
        self, mock_zephyr_client, sample_created_resource
    ):
        """Test successful create_folder."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = sample_created_resource
            mock_client.post.return_value = mock_response

            from src.mcp_zephyr_scale_cloud.schemas.folder import CreateFolderRequest

            request = CreateFolderRequest(
                projectKey="TEST",
                name="New Folder",
                folderType="TEST_CASE",
                parentId=1,
            )

            result = await mock_zephyr_client.create_folder(request)

            assert result.is_valid
            assert result.data.id == 123
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            request_data = call_args[1]["json"]
            assert request_data["projectKey"] == "TEST"
            assert request_data["name"] == "New Folder"
            assert request_data["folderType"] == "TEST_CASE"
            assert request_data["parentId"] == 1

    @pytest.mark.asyncio
    async def test_update_test_case_success(self, mock_zephyr_client):
        """Test successful update_test_case."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_client.put.return_value = mock_response

            from src.mcp_zephyr_scale_cloud.schemas.test_case import TestCaseUpdateInput

            update_input = TestCaseUpdateInput(
                name="Updated test case",
                objective="Updated objective",
                status_name="Ready for Review",
                custom_fields={"Component": "Test", "Version": "v2.0"},
            )

            result = await mock_zephyr_client.update_test_case(
                test_case_key="PROJ-T123", test_case_input=update_input
            )

            assert result.is_valid
            assert result.data is None  # PUT returns no content
            mock_client.put.assert_called_once()
            call_args = mock_client.put.call_args

            # Check URL
            assert call_args[0][0].endswith("/testcases/PROJ-T123")

            # Check request data - should contain only the updated fields
            request_data = call_args[1]["json"]
            assert request_data["name"] == "Updated test case"
            assert request_data["objective"] == "Updated objective"
            assert request_data["statusName"] == "Ready for Review"
            assert request_data["customFields"] == {
                "Component": "Test",
                "Version": "v2.0",
            }

    @pytest.mark.asyncio
    async def test_update_test_case_partial_update(self, mock_zephyr_client):
        """Test update_test_case with partial update."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_client.put.return_value = mock_response

            from src.mcp_zephyr_scale_cloud.schemas.test_case import TestCaseUpdateInput

            update_input = TestCaseUpdateInput(status_name="Completed")

            result = await mock_zephyr_client.update_test_case(
                test_case_key="PROJ-T123", test_case_input=update_input
            )

            assert result.is_valid
            assert result.data is None
            mock_client.put.assert_called_once()
            call_args = mock_client.put.call_args

            # Check request data - should contain only the updated field
            request_data = call_args[1]["json"]
            assert request_data["statusName"] == "Completed"
            # Other fields should not be present in the request
            assert "name" not in request_data
            assert "objective" not in request_data
            assert "estimatedTime" not in request_data

    @pytest.mark.asyncio
    async def test_update_test_case_http_error(self, mock_zephyr_client):
        """Test update_test_case with HTTP error."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock HTTP error
            import httpx

            mock_client.put.side_effect = httpx.HTTPError("Test case not found")

            from src.mcp_zephyr_scale_cloud.schemas.test_case import TestCaseUpdateInput

            update_input = TestCaseUpdateInput(name="Updated test case")

            result = await mock_zephyr_client.update_test_case(
                test_case_key="PROJ-T999", test_case_input=update_input
            )

            assert not result.is_valid
            assert "Failed to update test case PROJ-T999" in result.errors[0]
            assert "Test case not found" in result.errors[0]
