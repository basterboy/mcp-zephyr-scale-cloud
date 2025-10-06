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
        # Mock the get_test_case call first
        from src.mcp_zephyr_scale_cloud.schemas.common import ProjectLink
        from src.mcp_zephyr_scale_cloud.schemas.priority import PriorityLink
        from src.mcp_zephyr_scale_cloud.schemas.status import StatusLink
        from src.mcp_zephyr_scale_cloud.schemas.test_case import TestCase
        from src.mcp_zephyr_scale_cloud.utils.validation import ValidationResult

        mock_current_test_case = TestCase(
            id=123,
            key="PROJ-T123",
            name="Original test case",
            project=ProjectLink(id=1, self="http://example.com"),
            priority=PriorityLink(id=1, self="http://example.com"),
            status=StatusLink(id=1, self="http://example.com"),
            objective="Original objective",
            precondition="Original precondition",
        )

        # Mock the get_test_case method to return the current test case
        with patch.object(mock_zephyr_client, "get_test_case") as mock_get:
            mock_get.return_value = ValidationResult(True, data=mock_current_test_case)

            with patch("httpx.AsyncClient") as mock_client_class:
                mock_client = AsyncMock()
                mock_client_class.return_value.__aenter__.return_value = mock_client

                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.raise_for_status.return_value = None
                mock_client.put.return_value = mock_response

                from src.mcp_zephyr_scale_cloud.schemas.test_case import (
                    TestCaseUpdateInput,
                )

                update_input = TestCaseUpdateInput(
                    name="Updated test case",
                    objective="Updated objective",
                    status={"id": 123},
                    custom_fields={"Component": "Test", "Version": "v2.0"},
                )

                result = await mock_zephyr_client.update_test_case(
                    test_case_key="PROJ-T123", test_case_input=update_input
                )

                assert result.is_valid
                assert result.data is None  # PUT returns no content
                mock_get.assert_called_once_with("PROJ-T123")
                mock_client.put.assert_called_once()
                call_args = mock_client.put.call_args

                # Check URL
                assert call_args[0][0].endswith("/testcases/PROJ-T123")

                # Check request data - should contain merged current + update data
                request_data = call_args[1]["json"]
                assert request_data["name"] == "Updated test case"  # Updated
                assert request_data["objective"] == "Updated objective"  # Updated
                assert request_data["precondition"] == "Original precondition"
                assert request_data["status"] == {"id": 123}  # Updated
                assert request_data["customFields"] == {
                    "Component": "Test",
                    "Version": "v2.0",
                }  # Updated

    @pytest.mark.asyncio
    async def test_update_test_case_partial_update(self, mock_zephyr_client):
        """Test update_test_case with partial update."""
        # Mock the get_test_case call first
        from src.mcp_zephyr_scale_cloud.schemas.common import ProjectLink
        from src.mcp_zephyr_scale_cloud.schemas.priority import PriorityLink
        from src.mcp_zephyr_scale_cloud.schemas.status import StatusLink
        from src.mcp_zephyr_scale_cloud.schemas.test_case import TestCase
        from src.mcp_zephyr_scale_cloud.utils.validation import ValidationResult

        mock_current_test_case = TestCase(
            id=123,
            key="PROJ-T123",
            name="Original test case",
            project=ProjectLink(id=1, self="http://example.com"),
            priority=PriorityLink(id=1, self="http://example.com"),
            status=StatusLink(id=1, self="http://example.com"),
            objective="Original objective",
        )

        # Mock the get_test_case method to return the current test case
        with patch.object(mock_zephyr_client, "get_test_case") as mock_get:
            mock_get.return_value = ValidationResult(True, data=mock_current_test_case)

            with patch("httpx.AsyncClient") as mock_client_class:
                mock_client = AsyncMock()
                mock_client_class.return_value.__aenter__.return_value = mock_client

                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.raise_for_status.return_value = None
                mock_client.put.return_value = mock_response

                from src.mcp_zephyr_scale_cloud.schemas.test_case import (
                    TestCaseUpdateInput,
                )

                update_input = TestCaseUpdateInput(status={"id": 456})

                result = await mock_zephyr_client.update_test_case(
                    test_case_key="PROJ-T123", test_case_input=update_input
                )

                assert result.is_valid
                assert result.data is None
                mock_get.assert_called_once_with("PROJ-T123")
                mock_client.put.assert_called_once()
                call_args = mock_client.put.call_args

                # Check request data - should contain merged current + update data
                request_data = call_args[1]["json"]
                assert request_data["status"] == {"id": 456}  # Updated
                assert request_data["name"] == "Original test case"  # From current
                assert request_data["objective"] == "Original objective"  # From current
                # Note: priority/status Link objects are not converted to names yet

    @pytest.mark.asyncio
    async def test_update_test_case_http_error(self, mock_zephyr_client):
        """Test update_test_case with HTTP error."""
        # Mock the get_test_case call to fail (simulating test case not found)
        from src.mcp_zephyr_scale_cloud.utils.validation import ValidationResult

        # Mock the get_test_case method to return an error
        with patch.object(mock_zephyr_client, "get_test_case") as mock_get:
            mock_get.return_value = ValidationResult(
                False, errors=["Test case not found"]
            )

            from src.mcp_zephyr_scale_cloud.schemas.test_case import TestCaseUpdateInput

            update_input = TestCaseUpdateInput(name="Updated test case")

            result = await mock_zephyr_client.update_test_case(
                test_case_key="PROJ-T999", test_case_input=update_input
            )

            assert not result.is_valid
            assert "Failed to get current test case PROJ-T999" in result.errors[0]
            assert "Test case not found" in result.errors[0]


class TestZephyrClientGetTestCases:
    """Test cases for get_test_cases method (traditional endpoint)."""

    @pytest.fixture
    def mock_zephyr_client(self):
        """Create a ZephyrClient instance with mocked config."""
        config = MagicMock()
        config.api_token = "test_token"
        config.base_url = "https://api.test.com/v2"
        return ZephyrClient(config)

    @pytest.mark.asyncio
    async def test_get_test_cases_success(self, mock_zephyr_client):
        """Test successful get_test_cases call."""
        from src.mcp_zephyr_scale_cloud.schemas.common import ProjectLink
        from src.mcp_zephyr_scale_cloud.schemas.priority import PriorityLink
        from src.mcp_zephyr_scale_cloud.schemas.status import StatusLink
        from src.mcp_zephyr_scale_cloud.schemas.test_case import (
            TestCase,
            TestCaseList,
        )

        # Mock test case data
        mock_test_case = TestCase(
            id=123,
            key="PROJ-T456",
            name="Test case",
            project=ProjectLink(id=1, self="http://example.com"),
            priority=PriorityLink(id=1, self="http://example.com"),
            status=StatusLink(id=1, self="http://example.com"),
        )

        mock_response_data = {
            "values": [mock_test_case.model_dump(by_alias=True, exclude_none=True)],
            "maxResults": 10,
            "startAt": 0,
            "next": "https://api.test.com/v2/testcases?startAt=10&maxResults=10",
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response

            result = await mock_zephyr_client.get_test_cases(
                project_key="PROJ", folder_id=123, max_results=10, start_at=0
            )

            assert result.is_valid
            assert isinstance(result.data, TestCaseList)
            assert len(result.data.values) == 1
            assert result.data.values[0].key == "PROJ-T456"
            assert result.data.max_results == 10
            assert result.data.start_at == 0

            # Verify API call
            mock_client.get.assert_called_once()
            call_args = mock_client.get.call_args
            assert call_args[0][0] == "https://api.test.com/v2/testcases"
            assert call_args[1]["params"]["projectKey"] == "PROJ"
            assert call_args[1]["params"]["folderId"] == 123
            assert call_args[1]["params"]["maxResults"] == 10
            assert call_args[1]["params"]["startAt"] == 0

    @pytest.mark.asyncio
    async def test_get_test_cases_no_filters(self, mock_zephyr_client):
        """Test get_test_cases with no filters."""
        mock_response_data = {
            "values": [],
            "maxResults": 10,
            "startAt": 0,
            "next": None,
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response

            result = await mock_zephyr_client.get_test_cases()

            assert result.is_valid
            assert len(result.data.values) == 0
            assert result.data.max_results == 10
            assert result.data.start_at == 0

            # Verify API call parameters - no project_key or folder_id
            call_args = mock_client.get.call_args
            params = call_args[1]["params"]
            assert "projectKey" not in params
            assert "folderId" not in params
            assert params["maxResults"] == 10
            assert params["startAt"] == 0

    @pytest.mark.asyncio
    async def test_get_test_cases_invalid_pagination(self, mock_zephyr_client):
        """Test get_test_cases with invalid pagination parameters."""
        result = await mock_zephyr_client.get_test_cases(max_results=-1, start_at=-5)

        assert not result.is_valid
        assert len(result.errors) == 2
        assert "max_results must be at least 1" in result.errors
        assert "start_at must be non-negative" in result.errors

    @pytest.mark.asyncio
    async def test_get_test_cases_http_error(self, mock_zephyr_client):
        """Test get_test_cases HTTP error handling."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock HTTP error
            mock_client.get.side_effect = httpx.HTTPStatusError(
                "Not Found", request=MagicMock(), response=MagicMock(status_code=404)
            )

            result = await mock_zephyr_client.get_test_cases()

            assert not result.is_valid
            assert "Failed to get test cases" in result.errors[0]


class TestZephyrClientTestCycles:
    """Test Zephyr client test cycle methods."""

    @pytest.mark.asyncio
    async def test_get_test_cycles_success(self, mock_zephyr_client):
        """Test successful retrieval of test cycles."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "maxResults": 10,
                "startAt": 0,
                "total": 2,
                "isLast": True,
                "values": [
                    {
                        "id": 1,
                        "key": "PROJ-R1",
                        "name": "Sprint 1 Testing",
                        "project": {"id": 10000, "key": "PROJ"},
                        "status": {"id": 1, "name": "In Progress"},
                    },
                    {
                        "id": 2,
                        "key": "PROJ-R2",
                        "name": "Sprint 2 Testing",
                        "project": {"id": 10000, "key": "PROJ"},
                        "status": {"id": 1, "name": "In Progress"},
                    },
                ],
            }
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response

            result = await mock_zephyr_client.get_test_cycles(
                project_key="PROJ", max_results=10, start_at=0
            )

            assert result.is_valid
            assert len(result.data.values) == 2
            assert result.data.values[0].key == "PROJ-R1"
            assert result.data.values[1].key == "PROJ-R2"

    @pytest.mark.asyncio
    async def test_get_test_cycle_success(self, mock_zephyr_client):
        """Test successful retrieval of a specific test cycle."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "id": 1,
                "key": "PROJ-R1",
                "name": "Sprint 1 Testing",
                "project": {"id": 10000, "key": "PROJ"},
                "status": {"id": 1, "name": "In Progress"},
                "description": "Testing for sprint 1",
            }
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response

            result = await mock_zephyr_client.get_test_cycle(test_cycle_key="PROJ-R1")

            assert result.is_valid
            assert result.data.key == "PROJ-R1"
            assert result.data.name == "Sprint 1 Testing"
            assert result.data.description == "Testing for sprint 1"

    @pytest.mark.asyncio
    async def test_create_test_cycle_success(self, mock_zephyr_client):
        """Test successful creation of a test cycle."""
        from mcp_zephyr_scale_cloud.schemas.test_cycle import TestCycleInput

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.json.return_value = {"id": 1, "key": "PROJ-R1"}
            mock_response.raise_for_status.return_value = None
            mock_client.post.return_value = mock_response

            test_cycle_input = TestCycleInput(
                project_key="PROJ", name="Sprint 1 Testing"
            )
            result = await mock_zephyr_client.create_test_cycle(
                test_cycle_input=test_cycle_input
            )

            assert result.is_valid
            assert result.data.id == 1
            assert result.data.key == "PROJ-R1"

    @pytest.mark.asyncio
    async def test_update_test_cycle_success_with_body(self, mock_zephyr_client):
        """Test successful update of a test cycle with response body."""
        from mcp_zephyr_scale_cloud.schemas.test_cycle import TestCycle

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "id": 1,
                "key": "PROJ-R1",
                "name": "Updated Cycle",
                "project": {"id": 10000, "key": "PROJ"},
                "status": {"id": 1, "name": "In Progress"},
            }
            mock_response.raise_for_status.return_value = None
            mock_client.put.return_value = mock_response

            test_cycle = TestCycle(
                id=1,
                key="PROJ-R1",
                name="Updated Cycle",
                project={"id": 10000, "key": "PROJ"},
                status={"id": 1, "name": "In Progress"},
            )
            result = await mock_zephyr_client.update_test_cycle(
                test_cycle_key="PROJ-R1", test_cycle=test_cycle
            )

            assert result.is_valid
            assert result.data.name == "Updated Cycle"

    @pytest.mark.asyncio
    async def test_update_test_cycle_success_no_content(self, mock_zephyr_client):
        """Test successful update of a test cycle with 204 No Content."""
        from mcp_zephyr_scale_cloud.schemas.test_cycle import TestCycle

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 204
            mock_response.content = b""
            mock_response.raise_for_status.return_value = None
            mock_client.put.return_value = mock_response

            test_cycle = TestCycle(
                id=1,
                key="PROJ-R1",
                name="Updated Cycle",
                project={"id": 10000, "key": "PROJ"},
                status={"id": 1, "name": "In Progress"},
            )
            result = await mock_zephyr_client.update_test_cycle(
                test_cycle_key="PROJ-R1", test_cycle=test_cycle
            )

            assert result.is_valid
            assert result.data.key == "PROJ-R1"

    @pytest.mark.asyncio
    async def test_get_test_cycle_links_success(self, mock_zephyr_client):
        """Test successful retrieval of test cycle links."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "issueLinks": [{"id": 1, "issueId": 10001}],
                "webLinks": [{"id": 2, "url": "https://example.com"}],
            }
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response

            result = await mock_zephyr_client.get_test_cycle_links(
                test_cycle_key="PROJ-R1"
            )

            assert result.is_valid
            assert len(result.data.issues) == 1
            assert len(result.data.web_links) == 1

    @pytest.mark.asyncio
    async def test_create_test_cycle_issue_link_success(self, mock_zephyr_client):
        """Test successful creation of test cycle issue link."""
        from mcp_zephyr_scale_cloud.schemas.test_case import IssueLinkInput

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.json.return_value = {"id": 123}
            mock_response.raise_for_status.return_value = None
            mock_client.post.return_value = mock_response

            issue_link_input = IssueLinkInput(issueId=10001)
            result = await mock_zephyr_client.create_test_cycle_issue_link(
                test_cycle_key="PROJ-R1", issue_link_input=issue_link_input
            )

            assert result.is_valid
            assert result.data.id == 123

    @pytest.mark.asyncio
    async def test_create_test_cycle_issue_link_no_content(self, mock_zephyr_client):
        """Test successful creation of test cycle issue link with 204 No Content."""
        from mcp_zephyr_scale_cloud.schemas.test_case import IssueLinkInput

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 204
            mock_response.content = b""
            mock_response.raise_for_status.return_value = None
            mock_client.post.return_value = mock_response

            issue_link_input = IssueLinkInput(issueId=10001)
            result = await mock_zephyr_client.create_test_cycle_issue_link(
                test_cycle_key="PROJ-R1", issue_link_input=issue_link_input
            )

            assert result.is_valid
            assert result.data.id == 0

    @pytest.mark.asyncio
    async def test_create_test_cycle_web_link_success(self, mock_zephyr_client):
        """Test successful creation of test cycle web link."""
        from mcp_zephyr_scale_cloud.schemas.test_case import WebLinkInput

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.json.return_value = {"id": 456}
            mock_response.raise_for_status.return_value = None
            mock_client.post.return_value = mock_response

            web_link_input = WebLinkInput(url="https://example.com")
            result = await mock_zephyr_client.create_test_cycle_web_link(
                test_cycle_key="PROJ-R1", web_link_input=web_link_input
            )

            assert result.is_valid
            assert result.data.id == 456

    @pytest.mark.asyncio
    async def test_create_test_cycle_web_link_no_content(self, mock_zephyr_client):
        """Test successful creation of test cycle web link with 204 No Content."""
        from mcp_zephyr_scale_cloud.schemas.test_case import WebLinkInput

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 204
            mock_response.content = b""
            mock_response.raise_for_status.return_value = None
            mock_client.post.return_value = mock_response

            web_link_input = WebLinkInput(url="https://example.com")
            result = await mock_zephyr_client.create_test_cycle_web_link(
                test_cycle_key="PROJ-R1", web_link_input=web_link_input
            )

            assert result.is_valid
            assert result.data.id == 0


class TestZephyrClientTestPlans:
    """Test Zephyr client test plan methods."""

    @pytest.mark.asyncio
    async def test_get_test_plans_success(self, mock_zephyr_client):
        """Test successful retrieval of test plans."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "maxResults": 10,
                "startAt": 0,
                "total": 2,
                "isLast": True,
                "values": [
                    {
                        "id": 1,
                        "key": "PROJ-P1",
                        "name": "Integration Test Plan",
                        "project": {"id": 10000, "key": "PROJ"},
                        "status": {"id": 1, "name": "Draft"},
                    },
                    {
                        "id": 2,
                        "key": "PROJ-P2",
                        "name": "Regression Test Plan",
                        "project": {"id": 10000, "key": "PROJ"},
                        "status": {"id": 1, "name": "In Progress"},
                    },
                ],
            }
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response

            result = await mock_zephyr_client.get_test_plans(
                project_key="PROJ", max_results=10, start_at=0
            )

            assert result.is_valid
            assert len(result.data.values) == 2
            assert result.data.values[0].key == "PROJ-P1"
            assert result.data.values[1].key == "PROJ-P2"

    @pytest.mark.asyncio
    async def test_get_test_plan_success(self, mock_zephyr_client):
        """Test successful retrieval of a specific test plan."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "id": 1,
                "key": "PROJ-P1",
                "name": "Integration Test Plan",
                "project": {"id": 10000, "key": "PROJ"},
                "status": {"id": 1, "name": "Draft"},
                "objective": "Test all integration points",
            }
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response

            result = await mock_zephyr_client.get_test_plan(test_plan_key="PROJ-P1")

            assert result.is_valid
            assert result.data.key == "PROJ-P1"
            assert result.data.name == "Integration Test Plan"

    @pytest.mark.asyncio
    async def test_create_test_plan_success(self, mock_zephyr_client):
        """Test successful creation of a test plan."""
        from src.mcp_zephyr_scale_cloud.schemas.test_plan import TestPlanInput

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.json.return_value = {"id": 123, "key": "PROJ-P123"}
            mock_response.raise_for_status.return_value = None
            mock_client.post.return_value = mock_response

            test_plan_input = TestPlanInput(projectKey="PROJ", name="New Test Plan")
            result = await mock_zephyr_client.create_test_plan(
                test_plan_input=test_plan_input
            )

            assert result.is_valid
            assert result.data.id == 123

    @pytest.mark.asyncio
    async def test_create_test_plan_issue_link_success(self, mock_zephyr_client):
        """Test successful creation of test plan issue link."""
        from src.mcp_zephyr_scale_cloud.schemas.test_case import IssueLinkInput

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.json.return_value = {"id": 456}
            mock_response.raise_for_status.return_value = None
            mock_client.post.return_value = mock_response

            issue_link_input = IssueLinkInput(issueId=12345)
            result = await mock_zephyr_client.create_test_plan_issue_link(
                test_plan_key="PROJ-P1", issue_link_input=issue_link_input
            )

            assert result.is_valid
            assert result.data.id == 456

    @pytest.mark.asyncio
    async def test_create_test_plan_issue_link_no_content(self, mock_zephyr_client):
        """Test test plan issue link creation with 204 No Content response."""
        from src.mcp_zephyr_scale_cloud.schemas.test_case import IssueLinkInput

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 204
            mock_response.content = b""
            mock_response.raise_for_status.return_value = None
            mock_client.post.return_value = mock_response

            issue_link_input = IssueLinkInput(issueId=12345)
            result = await mock_zephyr_client.create_test_plan_issue_link(
                test_plan_key="PROJ-P1", issue_link_input=issue_link_input
            )

            assert result.is_valid
            assert result.data.id == 0

    @pytest.mark.asyncio
    async def test_create_test_plan_web_link_success(self, mock_zephyr_client):
        """Test successful creation of test plan web link."""
        from src.mcp_zephyr_scale_cloud.schemas.test_plan import (
            WebLinkInputWithMandatoryDescription,
        )

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.json.return_value = {"id": 789}
            mock_response.raise_for_status.return_value = None
            mock_client.post.return_value = mock_response

            web_link_input = WebLinkInputWithMandatoryDescription(
                url="https://example.com", description="Test link"
            )
            result = await mock_zephyr_client.create_test_plan_web_link(
                test_plan_key="PROJ-P1", web_link_input=web_link_input
            )

            assert result.is_valid
            assert result.data.id == 789

    @pytest.mark.asyncio
    async def test_create_test_plan_test_cycle_link_success(self, mock_zephyr_client):
        """Test successful creation of test plan to test cycle link."""
        from src.mcp_zephyr_scale_cloud.schemas.test_plan import (
            TestPlanTestCycleLinkInput,
        )

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.json.return_value = {"id": 999}
            mock_response.raise_for_status.return_value = None
            mock_client.post.return_value = mock_response

            link_input = TestPlanTestCycleLinkInput(testCycleIdOrKey="456")
            result = await mock_zephyr_client.create_test_plan_test_cycle_link(
                test_plan_key="PROJ-P1", test_cycle_link_input=link_input
            )

            assert result.is_valid
            assert result.data.id == 999

    @pytest.mark.asyncio
    async def test_create_test_plan_test_cycle_link_no_content(
        self, mock_zephyr_client
    ):
        """Test test plan test cycle link creation with 204 No Content response."""
        from src.mcp_zephyr_scale_cloud.schemas.test_plan import (
            TestPlanTestCycleLinkInput,
        )

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 204
            mock_response.content = b""
            mock_response.raise_for_status.return_value = None
            mock_client.post.return_value = mock_response

            link_input = TestPlanTestCycleLinkInput(testCycleIdOrKey="456")
            result = await mock_zephyr_client.create_test_plan_test_cycle_link(
                test_plan_key="PROJ-P1", test_cycle_link_input=link_input
            )

            assert result.is_valid
            assert result.data.id == 0
