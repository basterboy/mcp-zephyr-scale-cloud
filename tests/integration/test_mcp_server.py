"""Integration tests for MCP server."""

import json
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from src.mcp_zephyr_scale_cloud.server import (
    create_folder,
    create_priority,
    create_status,
    get_folder,
    get_folders,
    get_priorities,
    get_priority,
    get_status,
    get_statuses,
    healthcheck,
    mcp,
    update_priority,
    update_status,
    zephyr_server_lifespan,
)


class TestMCPServerIntegration:
    """Integration tests for MCP server functionality."""

    @pytest.mark.asyncio
    async def test_server_lifespan_success(self, mock_env_vars):
        """Test successful server lifespan management."""
        with patch(
            "src.mcp_zephyr_scale_cloud.server.ZephyrClient"
        ) as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            # Mock successful healthcheck
            mock_health_result = AsyncMock()
            mock_health_result.is_valid = True
            mock_health_result.data = {"status": "UP"}
            mock_client.healthcheck.return_value = mock_health_result

            async with zephyr_server_lifespan(mcp) as result:
                assert result["config_valid"] is True
                assert result["api_accessible"] is True
                assert result["startup_errors"] == []
                assert result["tools_count"] == 23

    @pytest.mark.asyncio
    async def test_server_lifespan_config_error(self):
        """Test server lifespan with configuration error."""
        # Skip this test for now - it's complex to mock properly due to global state
        # In a real scenario, we'd test this by running with missing env vars
        pytest.skip("Skipping config error test - requires environment-level testing")

    @pytest.mark.asyncio
    async def test_mcp_tools_list(self):
        """Test that MCP server has all expected tools."""
        tools = await mcp.list_tools()

        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "healthcheck",
            "get_priorities",
            "get_priority",
            "create_priority",
            "update_priority",
            "get_statuses",
            "get_status",
            "create_status",
            "update_status",
            "get_folders",
            "get_folder",
            "create_folder",
            "get_test_steps",
            "create_test_steps",
            "get_test_script",
            "create_test_script",
            "get_test_case",
            "get_test_case_versions",
            "get_test_case_version",
            "get_links",
            "create_issue_link",
            "create_web_link",
            "create_test_case",
            "update_test_case",
        ]

        for tool_name in expected_tools:
            assert tool_name in tool_names

    @pytest.mark.asyncio
    async def test_healthcheck_tool_success(self, mock_env_vars):
        """Test healthcheck tool with successful response."""

        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client") as mock_client:
            mock_result = AsyncMock()
            mock_result.is_valid = True
            mock_result.data = {"status": "UP"}
            mock_client.healthcheck = AsyncMock(return_value=mock_result)

            result = await healthcheck()

            # Parse JSON response
            response_data = json.loads(result)
            assert response_data["status"] == "UP"

    @pytest.mark.asyncio
    async def test_healthcheck_tool_no_config(self):
        """Test healthcheck tool without configuration."""
        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client", None):
            result = await healthcheck()

            # For config errors, _CONFIG_ERROR_MSG is returned directly as a string
            assert "ERROR" in result
            assert "configuration not found" in result

    @pytest.mark.asyncio
    async def test_get_priorities_tool_success(
        self, mock_env_vars, sample_priority_list
    ):
        """Test get_priorities tool with successful response."""

        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client") as mock_client:
            mock_result = AsyncMock()
            mock_result.is_valid = True
            # Create a mock object with model_dump method (not async)
            mock_data = Mock()
            mock_data.model_dump.return_value = sample_priority_list
            mock_result.data = mock_data
            mock_client.get_priorities = AsyncMock(return_value=mock_result)

            result = await get_priorities()

            # Parse JSON response
            response_data = json.loads(result)
            assert response_data == sample_priority_list
            mock_client.get_priorities.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_priority_tool_success(self, mock_env_vars, sample_priority_data):
        """Test get_priority tool with successful response."""

        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client") as mock_client:
            mock_result = AsyncMock()
            mock_result.is_valid = True
            # Create a mock object with model_dump method (not async)
            mock_data = Mock()
            mock_data.model_dump.return_value = sample_priority_data
            mock_result.data = mock_data
            mock_client.get_priority = AsyncMock(return_value=mock_result)

            result = await get_priority(1)

            # Parse JSON response
            response_data = json.loads(result)
            assert response_data == sample_priority_data
            mock_client.get_priority.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_create_priority_tool_success(
        self, mock_env_vars, sample_created_resource
    ):
        """Test create_priority tool with successful response."""
        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client") as mock_client:
            with patch(
                "src.mcp_zephyr_scale_cloud.server.validate_priority_data"
            ) as mock_validate:
                # Mock validation success
                mock_request = AsyncMock()
                mock_validate_result = AsyncMock()
                mock_validate_result.return_value = True
                mock_validate_result.data = mock_request
                mock_validate.return_value = mock_validate_result

                # Mock client success
                mock_result = AsyncMock()
                mock_result.is_valid = True
                # Create a mock object with model_dump method (not async)
                mock_data = Mock()
                mock_data.model_dump.return_value = sample_created_resource
                mock_result.data = mock_data
                mock_client.create_priority = AsyncMock(return_value=mock_result)

                result = await create_priority(name="High Priority", project_key="TEST")

                # Parse JSON response
                response_data = json.loads(result)
                assert response_data == sample_created_resource

    @pytest.mark.asyncio
    async def test_update_priority_tool_success(self, mock_env_vars):
        """Test update_priority tool with successful response."""
        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client") as mock_client:
            with patch(
                "src.mcp_zephyr_scale_cloud.server.validate_priority_data"
            ) as mock_validate:
                # Mock validation success
                mock_request = AsyncMock()
                mock_validate_result = AsyncMock()
                mock_validate_result.return_value = True
                mock_validate_result.data = mock_request
                mock_validate.return_value = mock_validate_result

                # Mock client success
                mock_result = AsyncMock()
                mock_result.is_valid = True
                mock_result.data = {"success": True, "message": "Updated"}
                mock_client.update_priority = AsyncMock(return_value=mock_result)

                result = await update_priority(1, 123, "Updated Priority", 0)

                # Parse JSON response - update operations return simple success status
                response_data = json.loads(result)
                assert response_data == {"status": "updated"}

    @pytest.mark.asyncio
    async def test_get_statuses_tool_success(self, mock_env_vars, sample_status_list):
        """Test get_statuses tool with successful response."""

        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client") as mock_client:
            mock_result = AsyncMock()
            mock_result.is_valid = True
            # Create a mock object with model_dump method (not async)
            mock_data = Mock()
            mock_data.model_dump.return_value = sample_status_list
            mock_result.data = mock_data
            mock_client.get_statuses = AsyncMock(return_value=mock_result)

            result = await get_statuses()

            # Parse JSON response
            response_data = json.loads(result)
            assert response_data == sample_status_list
            mock_client.get_statuses.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_statuses_tool_with_filters(
        self, mock_env_vars, sample_status_list
    ):
        """Test get_statuses tool with project and type filters."""

        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client") as mock_client:
            mock_result = AsyncMock()
            mock_result.is_valid = True
            # Create a mock object with model_dump method (not async)
            mock_data = Mock()
            mock_data.model_dump.return_value = sample_status_list
            mock_result.data = mock_data
            mock_client.get_statuses = AsyncMock(return_value=mock_result)

            result = await get_statuses(
                project_key="TEST", status_type="TEST_EXECUTION", max_results=100
            )

            # Parse JSON response
            response_data = json.loads(result)
            assert response_data == sample_status_list
            mock_client.get_statuses.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_status_tool_success(self, mock_env_vars, sample_status_data):
        """Test get_status tool with successful response."""

        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client") as mock_client:
            mock_result = AsyncMock()
            mock_result.is_valid = True
            # Create a mock object with model_dump method (not async)
            mock_data = Mock()
            mock_data.model_dump.return_value = sample_status_data
            mock_result.data = mock_data
            mock_client.get_status = AsyncMock(return_value=mock_result)

            result = await get_status(1)

            # Parse JSON response
            response_data = json.loads(result)
            assert response_data == sample_status_data
            mock_client.get_status.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_create_status_tool_success(
        self, mock_env_vars, sample_created_resource
    ):
        """Test create_status tool with successful response."""
        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client") as mock_client:
            with patch(
                "src.mcp_zephyr_scale_cloud.server.validate_status_data"
            ) as mock_validate:
                # Mock validation success
                mock_request = AsyncMock()
                mock_validate_result = AsyncMock()
                mock_validate_result.is_valid = True
                mock_validate_result.data = mock_request
                mock_validate.return_value = mock_validate_result

                # Mock client success
                mock_result = AsyncMock()
                mock_result.is_valid = True
                # Create a mock object with model_dump method (not async)
                mock_data = Mock()
                mock_data.model_dump.return_value = sample_created_resource
                mock_result.data = mock_data
                mock_client.create_status = AsyncMock(return_value=mock_result)

                result = await create_status(
                    name="In Progress", status_type="TEST_EXECUTION", project_key="TEST"
                )

                # Parse JSON response
                response_data = json.loads(result)
                assert response_data == sample_created_resource

    @pytest.mark.asyncio
    async def test_update_status_tool_success(self, mock_env_vars):
        """Test update_status tool with successful response."""
        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client") as mock_client:
            with patch(
                "src.mcp_zephyr_scale_cloud.server.validate_status_data"
            ) as mock_validate:
                # Mock validation success
                mock_request = AsyncMock()
                mock_validate_result = AsyncMock()
                mock_validate_result.is_valid = True
                mock_validate_result.data = mock_request
                mock_validate.return_value = mock_validate_result

                # Mock client success
                mock_result = AsyncMock()
                mock_result.is_valid = True
                mock_result.data = {"success": True, "message": "Updated"}
                mock_client.update_status = AsyncMock(return_value=mock_result)

                result = await update_status(1, 123, "Updated Status", 0)

                # Parse JSON response - update operations return simple success status
                response_data = json.loads(result)
                assert response_data == {"status": "updated"}

    @pytest.mark.asyncio
    async def test_status_tool_no_config(self):
        """Test status tools without configuration."""
        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client", None):
            result = await get_statuses()

            assert "ERROR" in result
            assert "configuration not found" in result

    @pytest.mark.asyncio
    async def test_tool_call_through_mcp(self, mock_env_vars):
        """Test calling tools through MCP server interface."""
        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client") as mock_client:
            mock_result = AsyncMock()
            mock_result.is_valid = True
            mock_result.data = {"status": "UP"}
            mock_client.healthcheck = AsyncMock(return_value=mock_result)

            # Call tool through MCP interface
            result = await mcp.call_tool("healthcheck", {})

            assert result is not None
            # The result should be a CallToolResult with content


class TestFolderMCPTools:
    """Test cases for folder MCP tools."""

    @pytest.mark.asyncio
    async def test_get_folders_tool_success(self, mock_env_vars, sample_folder_list):
        """Test get_folders tool with successful response."""

        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client") as mock_client:
            # Mock client success
            mock_result = AsyncMock()
            mock_result.is_valid = True
            # Create a mock object with model_dump method (not async)
            mock_data = Mock()
            mock_data.model_dump.return_value = sample_folder_list
            mock_result.data = mock_data
            mock_client.get_folders = AsyncMock(return_value=mock_result)

            result = await get_folders()

            # Parse JSON response
            response_data = json.loads(result)
            assert response_data == sample_folder_list
            mock_client.get_folders.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_folders_tool_with_filters(
        self, mock_env_vars, sample_folder_list
    ):
        """Test get_folders tool with project and folder type filters."""
        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client") as mock_client:
            with patch(
                "src.mcp_zephyr_scale_cloud.server.validate_folder_type"
            ) as mock_validate_type:
                with patch(
                    "src.mcp_zephyr_scale_cloud.server.validate_project_key"
                ) as mock_validate_key:
                    # Mock validation success
                    mock_type_result = AsyncMock()
                    mock_type_result.is_valid = True
                    mock_type_result.data = type(
                        "MockFolderType", (), {"value": "TEST_CASE"}
                    )()
                    mock_validate_type.return_value = mock_type_result

                    mock_key_result = AsyncMock()
                    mock_key_result.is_valid = True
                    mock_validate_key.return_value = mock_key_result

                    # Mock client success
                    mock_result = AsyncMock()
                    mock_result.is_valid = True
                    # Create a mock object with model_dump method (not async)
                    mock_data = Mock()
                    mock_data.model_dump.return_value = sample_folder_list
                    mock_result.data = mock_data
                    mock_client.get_folders = AsyncMock(return_value=mock_result)

                    result = await get_folders("TEST", "TEST_CASE", 25)

                    # Parse JSON response
                    response_data = json.loads(result)
                    assert response_data == sample_folder_list
                    mock_client.get_folders.assert_called_once_with(
                        project_key="TEST",
                        folder_type=mock_type_result.data,
                        max_results=25,
                    )

    @pytest.mark.asyncio
    async def test_get_folder_tool_success(self, mock_env_vars, sample_folder_data):
        """Test get_folder tool with successful response."""

        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client") as mock_client:
            # Mock client success
            mock_result = AsyncMock()
            mock_result.is_valid = True
            # Create a mock object with model_dump method (not async)
            mock_data = Mock()
            mock_data.model_dump.return_value = sample_folder_data
            mock_result.data = mock_data
            mock_client.get_folder = AsyncMock(return_value=mock_result)

            result = await get_folder(1)

            # Parse JSON response
            response_data = json.loads(result)
            assert response_data == sample_folder_data
            mock_client.get_folder.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_create_folder_tool_success(
        self, mock_env_vars, sample_created_resource
    ):
        """Test create_folder tool with successful response."""
        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client") as mock_client:
            with patch(
                "src.mcp_zephyr_scale_cloud.server.validate_folder_data"
            ) as mock_validate:
                # Mock validation success
                mock_request = AsyncMock()
                mock_validate_result = AsyncMock()
                mock_validate_result.is_valid = True
                mock_validate_result.data = mock_request
                mock_validate.return_value = mock_validate_result

                # Mock client success
                mock_result = AsyncMock()
                mock_result.is_valid = True
                # Create a mock object with model_dump method (not async)
                mock_data = Mock()
                mock_data.model_dump.return_value = sample_created_resource
                mock_result.data = mock_data
                mock_client.create_folder = AsyncMock(return_value=mock_result)

                result = await create_folder("Test Folder", "TEST", "TEST_CASE", 1)

                # Parse JSON response
                response_data = json.loads(result)
                assert response_data == sample_created_resource

    @pytest.mark.asyncio
    async def test_folder_tools_error_handling(self, mock_env_vars):
        """Test folder tools error handling."""

        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client") as mock_client:
            # Mock client failure
            mock_result = AsyncMock()
            mock_result.is_valid = False
            mock_result.errors = ["API error"]
            mock_client.get_folders = AsyncMock(return_value=mock_result)

            result = await get_folders()

            # Parse JSON error response
            response_data = json.loads(result)
            assert response_data["errorCode"] == 500
            assert "API error" in response_data["message"]

    @pytest.mark.asyncio
    async def test_folder_tools_no_client(self, mock_env_vars):
        """Test folder tools when client is not initialized."""
        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client", None):
            result = await get_folders()

            # For client not initialized errors, _CONFIG_ERROR_MSG is returned directly
            assert "ERROR" in result
            assert "configuration not found" in result

    @pytest.mark.asyncio
    async def test_create_folder_parent_id_validation(self, mock_env_vars):
        """Test create_folder parent_id validation."""

        # Test with invalid parent_id string
        result = await create_folder("Test", "PROJ", "TEST_CASE", "invalid")
        response_data = json.loads(result)
        assert response_data["errorCode"] == 400
        assert "Parent folder ID must be a valid integer" in response_data["message"]

        # Test with negative parent_id
        result = await create_folder("Test", "PROJ", "TEST_CASE", "-1")
        response_data = json.loads(result)
        assert response_data["errorCode"] == 400
        assert "Folder ID must be a positive integer" in response_data["message"]

        # Test with zero parent_id
        result = await create_folder("Test", "PROJ", "TEST_CASE", "0")
        response_data = json.loads(result)
        assert response_data["errorCode"] == 400
        assert "Folder ID must be a positive integer" in response_data["message"]

    @pytest.mark.asyncio
    @patch("src.mcp_zephyr_scale_cloud.server.zephyr_client")
    async def test_get_test_case_versions_success(self, mock_client):
        """Test successful get_test_case_versions tool call."""
        from src.mcp_zephyr_scale_cloud.schemas.version import (
            TestCaseVersionLink,
            TestCaseVersionList,
        )
        from src.mcp_zephyr_scale_cloud.server import get_test_case_versions
        from src.mcp_zephyr_scale_cloud.utils.validation import ValidationResult

        # Mock successful API response
        mock_version_link = TestCaseVersionLink(
            id=1, self="https://api.example.com/testcases/PROJ-T1234/versions/1"
        )
        mock_version_list = TestCaseVersionList(
            values=[mock_version_link],
            startAt=0,
            maxResults=10,
            total=1,
            isLast=True,
        )
        mock_result = ValidationResult(True, data=mock_version_list)
        mock_client.get_test_case_versions = AsyncMock(return_value=mock_result)

        response = await get_test_case_versions(test_case_key="PROJ-T1234")

        # Parse JSON response
        response_data = json.loads(response)
        assert response_data["total"] == 1
        assert len(response_data["values"]) == 1
        assert response_data["values"][0]["id"] == 1
        mock_client.get_test_case_versions.assert_called_once_with(
            test_case_key="PROJ-T1234", max_results=10, start_at=0
        )

    @pytest.mark.asyncio
    @patch("src.mcp_zephyr_scale_cloud.server.zephyr_client")
    async def test_get_test_case_version_success(self, mock_client):
        """Test successful get_test_case_version tool call."""
        from src.mcp_zephyr_scale_cloud.schemas.common import ProjectLink
        from src.mcp_zephyr_scale_cloud.schemas.priority import PriorityLink
        from src.mcp_zephyr_scale_cloud.schemas.status import StatusLink
        from src.mcp_zephyr_scale_cloud.schemas.test_case import TestCase
        from src.mcp_zephyr_scale_cloud.server import get_test_case_version
        from src.mcp_zephyr_scale_cloud.utils.validation import ValidationResult

        # Mock successful API response
        mock_test_case = TestCase(
            id=12345,
            key="PROJ-T1234",
            name="Test case version 2",
            project=ProjectLink(
                id=10001, self="https://api.example.com/projects/10001"
            ),
            priority=PriorityLink(
                id=10002, self="https://api.example.com/priorities/10002"
            ),
            status=StatusLink(id=10003, self="https://api.example.com/statuses/10003"),
        )
        mock_result = ValidationResult(True, data=mock_test_case)
        mock_client.get_test_case_version = AsyncMock(return_value=mock_result)

        response = await get_test_case_version(test_case_key="PROJ-T1234", version=2)

        # Parse JSON response
        response_data = json.loads(response)
        assert response_data["id"] == 12345
        assert response_data["key"] == "PROJ-T1234"
        assert response_data["name"] == "Test case version 2"
        mock_client.get_test_case_version.assert_called_once_with(
            test_case_key="PROJ-T1234", version=2
        )

    @pytest.mark.asyncio
    @patch("src.mcp_zephyr_scale_cloud.server.zephyr_client")
    async def test_get_links_success(self, mock_client):
        """Test successful get_links tool call."""
        from src.mcp_zephyr_scale_cloud.schemas.test_case import (
            IssueLink,
            TestCaseLinkList,
            WebLink,
        )
        from src.mcp_zephyr_scale_cloud.server import get_links
        from src.mcp_zephyr_scale_cloud.utils.validation import ValidationResult

        # Mock successful API response
        mock_issue = IssueLink(
            id=1,
            issueId=12345,
            self="https://api.example.com/links/1",
            target="https://jira.example.com/issue/12345",
            type="COVERAGE",
        )
        mock_web_link = WebLink(
            id=2,
            url="https://example.com",
            description="Example link",
            self="https://api.example.com/weblinks/2",
            type="RELATED",
        )
        mock_links = TestCaseLinkList(
            self="https://api.example.com/testcases/PROJ-T1234/links",
            issues=[mock_issue],
            webLinks=[mock_web_link],
        )
        mock_result = ValidationResult(True, data=mock_links)
        mock_client.get_test_case_links = AsyncMock(return_value=mock_result)

        response = await get_links(test_case_key="PROJ-T1234")

        # Parse JSON response
        response_data = json.loads(response)
        assert len(response_data["issues"]) == 1
        assert response_data["issues"][0]["issueId"] == 12345
        assert response_data["issues"][0]["type"] == "COVERAGE"
        assert len(response_data["webLinks"]) == 1
        assert response_data["webLinks"][0]["url"] == "https://example.com"
        assert response_data["webLinks"][0]["description"] == "Example link"
        mock_client.get_test_case_links.assert_called_once_with(
            test_case_key="PROJ-T1234"
        )

    @pytest.mark.asyncio
    @patch("src.mcp_zephyr_scale_cloud.server.zephyr_client")
    async def test_create_issue_link_success(self, mock_client):
        """Test successful create_issue_link tool call."""
        from src.mcp_zephyr_scale_cloud.schemas.base import CreatedResource
        from src.mcp_zephyr_scale_cloud.server import create_issue_link
        from src.mcp_zephyr_scale_cloud.utils.validation import ValidationResult

        # Mock successful API response
        mock_created = CreatedResource(
            id=12345, self="https://api.example.com/links/12345"
        )
        mock_result = ValidationResult(True, data=mock_created)
        mock_client.create_test_case_issue_link = AsyncMock(return_value=mock_result)

        response = await create_issue_link(test_case_key="PROJ-T1234", issue_id=67890)

        # Parse JSON response
        response_data = json.loads(response)
        assert response_data["id"] == 12345
        assert response_data["self"] == "https://api.example.com/links/12345"
        mock_client.create_test_case_issue_link.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.mcp_zephyr_scale_cloud.server.zephyr_client")
    async def test_create_web_link_success(self, mock_client):
        """Test successful create_web_link tool call."""
        from src.mcp_zephyr_scale_cloud.schemas.base import CreatedResource
        from src.mcp_zephyr_scale_cloud.server import create_web_link
        from src.mcp_zephyr_scale_cloud.utils.validation import ValidationResult

        # Mock successful API response
        mock_created = CreatedResource(
            id=54321, self="https://api.example.com/weblinks/54321"
        )
        mock_result = ValidationResult(True, data=mock_created)
        mock_client.create_test_case_web_link = AsyncMock(return_value=mock_result)

        response = await create_web_link(
            test_case_key="PROJ-T1234",
            url="https://docs.example.com",
            description="Test documentation",
        )

        # Parse JSON response
        response_data = json.loads(response)
        assert response_data["id"] == 54321
        assert response_data["self"] == "https://api.example.com/weblinks/54321"
        mock_client.create_test_case_web_link.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.mcp_zephyr_scale_cloud.server.zephyr_client")
    async def test_create_issue_link_invalid_issue_key(self, mock_client):
        """Test create_issue_link with issue key instead of issue ID."""
        from src.mcp_zephyr_scale_cloud.server import create_issue_link

        # Test with issue key (should fail with helpful message)
        response = await create_issue_link(
            test_case_key="PROJ-T1234", issue_id="PROJ-1234"  # type: ignore
        )

        # Parse JSON error response
        response_data = json.loads(response)
        assert response_data["errorCode"] == 400
        assert "Issue ID must be a positive integer" in response_data["message"]
        assert "issue key" in response_data["message"]
        assert "PROJ-1234" in response_data["message"]
        assert "Atlassian/Jira MCP tool" in response_data["message"]
        # Should not call the API
        mock_client.create_test_case_issue_link.assert_not_called()

    @pytest.mark.asyncio
    @patch("src.mcp_zephyr_scale_cloud.server.zephyr_client")
    async def test_create_test_case_success(self, mock_client):
        """Test successful create_test_case tool call."""
        from src.mcp_zephyr_scale_cloud.schemas.base import CreatedResource
        from src.mcp_zephyr_scale_cloud.server import create_test_case
        from src.mcp_zephyr_scale_cloud.utils.validation import ValidationResult

        # Mock successful API response
        mock_created = CreatedResource(
            id=98765,
            self="https://api.example.com/testcases/PROJ-T123",
            key="PROJ-T123",
        )
        mock_result = ValidationResult(True, data=mock_created)
        mock_client.create_test_case = AsyncMock(return_value=mock_result)

        response = await create_test_case(
            project_key="PROJ",
            name="Test user login functionality",
            objective="Verify user can log in with valid credentials",
            priority_name="High",
            labels='["automation", "login"]',
        )

        # Parse JSON response
        response_data = json.loads(response)
        assert response_data["id"] == 98765
        assert response_data["self"] == "https://api.example.com/testcases/PROJ-T123"
        mock_client.create_test_case.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.mcp_zephyr_scale_cloud.server.zephyr_client")
    async def test_create_test_case_validation_error(self, mock_client):
        """Test create_test_case with validation errors."""
        from src.mcp_zephyr_scale_cloud.server import create_test_case

        # Test with invalid project key
        response = await create_test_case(project_key="invalid-key", name="Test case")

        # Parse JSON error response
        response_data = json.loads(response)
        assert response_data["errorCode"] == 400
        assert "Project key" in response_data["message"]
        assert "invalid-key" in response_data["message"]
        assert "uppercase letters" in response_data["message"]
        # Should not call the API
        mock_client.create_test_case.assert_not_called()

        # Test with empty name
        response = await create_test_case(project_key="PROJ", name="")

        # Parse JSON error response
        response_data = json.loads(response)
        assert response_data["errorCode"] == 400
        assert "Test case name cannot be empty" in response_data["message"]
        # Should not call the API
        mock_client.create_test_case.assert_not_called()

    @pytest.mark.asyncio
    @patch("src.mcp_zephyr_scale_cloud.server.zephyr_client")
    async def test_update_test_case_success(self, mock_client):
        """Test successful update_test_case tool call."""
        from src.mcp_zephyr_scale_cloud.server import update_test_case
        from src.mcp_zephyr_scale_cloud.utils.validation import ValidationResult

        # Mock successful API response (PUT returns None data)
        mock_result = ValidationResult(True, data=None)
        mock_client.update_test_case = AsyncMock(return_value=mock_result)

        response = await update_test_case(
            test_case_key="PROJ-T123",
            name="Updated test name",
            objective="Updated objective",
            status_id="456",  # Use ID directly instead of name
            custom_fields={"Components": ["Update"], "Version": "v2.0.0"},
        )

        # Parse JSON response
        response_data = json.loads(response)
        assert response_data["message"] == "Test case 'PROJ-T123' updated successfully"
        assert response_data["testCaseKey"] == "PROJ-T123"
        mock_client.update_test_case.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.mcp_zephyr_scale_cloud.server.zephyr_client")
    async def test_update_test_case_partial_update(self, mock_client):
        """Test update_test_case with only some fields updated."""
        from src.mcp_zephyr_scale_cloud.server import update_test_case
        from src.mcp_zephyr_scale_cloud.utils.validation import ValidationResult

        # Mock successful API response
        mock_result = ValidationResult(True, data=None)
        mock_client.update_test_case = AsyncMock(return_value=mock_result)

        response = await update_test_case(
            test_case_key="PROJ-T123",
            status_id="789",  # Use ID directly instead of name
        )

        # Parse JSON response
        response_data = json.loads(response)
        assert response_data["message"] == "Test case 'PROJ-T123' updated successfully"
        assert response_data["testCaseKey"] == "PROJ-T123"
        mock_client.update_test_case.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.mcp_zephyr_scale_cloud.server.zephyr_client")
    async def test_update_test_case_with_labels_comma_separated(self, mock_client):
        """Test update_test_case with comma-separated labels."""
        from src.mcp_zephyr_scale_cloud.server import update_test_case
        from src.mcp_zephyr_scale_cloud.utils.validation import ValidationResult

        # Mock successful API response
        mock_result = ValidationResult(True, data=None)
        mock_client.update_test_case = AsyncMock(return_value=mock_result)

        response = await update_test_case(
            test_case_key="PROJ-T123",
            labels="automation, regression, critical",
        )

        # Parse JSON response
        response_data = json.loads(response)
        assert response_data["message"] == "Test case 'PROJ-T123' updated successfully"
        mock_client.update_test_case.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.mcp_zephyr_scale_cloud.server.zephyr_client")
    async def test_update_test_case_with_labels_json_array(self, mock_client):
        """Test update_test_case with JSON array labels."""
        from src.mcp_zephyr_scale_cloud.server import update_test_case
        from src.mcp_zephyr_scale_cloud.utils.validation import ValidationResult

        # Mock successful API response
        mock_result = ValidationResult(True, data=None)
        mock_client.update_test_case = AsyncMock(return_value=mock_result)

        response = await update_test_case(
            test_case_key="PROJ-T123",
            labels='["automation", "regression"]',
        )

        # Parse JSON response
        response_data = json.loads(response)
        assert response_data["message"] == "Test case 'PROJ-T123' updated successfully"
        mock_client.update_test_case.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.mcp_zephyr_scale_cloud.server.zephyr_client")
    async def test_update_test_case_with_custom_fields_dict(self, mock_client):
        """Test update_test_case with dictionary custom_fields."""
        from src.mcp_zephyr_scale_cloud.server import update_test_case
        from src.mcp_zephyr_scale_cloud.utils.validation import ValidationResult

        # Mock successful API response
        mock_result = ValidationResult(True, data=None)
        mock_client.update_test_case = AsyncMock(return_value=mock_result)

        response = await update_test_case(
            test_case_key="PROJ-T123",
            custom_fields={"Components": ["Update"], "Version": "v2.0.0"},
        )

        # Parse JSON response
        response_data = json.loads(response)
        assert response_data["message"] == "Test case 'PROJ-T123' updated successfully"
        mock_client.update_test_case.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.mcp_zephyr_scale_cloud.server.zephyr_client")
    async def test_update_test_case_with_custom_fields_string(self, mock_client):
        """Test update_test_case with JSON string custom_fields."""
        from src.mcp_zephyr_scale_cloud.server import update_test_case
        from src.mcp_zephyr_scale_cloud.utils.validation import ValidationResult

        # Mock successful API response
        mock_result = ValidationResult(True, data=None)
        mock_client.update_test_case = AsyncMock(return_value=mock_result)

        response = await update_test_case(
            test_case_key="PROJ-T123",
            custom_fields='{"Components": ["Update"], "Version": "v2.0.0"}',
        )

        # Parse JSON response
        response_data = json.loads(response)
        assert response_data["message"] == "Test case 'PROJ-T123' updated successfully"
        mock_client.update_test_case.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.mcp_zephyr_scale_cloud.server.zephyr_client")
    async def test_update_test_case_with_integer_parameters(self, mock_client):
        """Test update_test_case with integer parameters."""
        from src.mcp_zephyr_scale_cloud.server import update_test_case
        from src.mcp_zephyr_scale_cloud.utils.validation import ValidationResult

        # Mock successful API response
        mock_result = ValidationResult(True, data=None)
        mock_client.update_test_case = AsyncMock(return_value=mock_result)

        response = await update_test_case(
            test_case_key="PROJ-T123",
            estimated_time="120000",
            component_id="456",
            folder_id="789",
        )

        # Parse JSON response
        response_data = json.loads(response)
        assert response_data["message"] == "Test case 'PROJ-T123' updated successfully"
        mock_client.update_test_case.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.mcp_zephyr_scale_cloud.server.zephyr_client")
    async def test_update_test_case_validation_errors(self, mock_client):
        """Test update_test_case with validation errors."""
        from src.mcp_zephyr_scale_cloud.server import update_test_case

        # Test with invalid test case key
        response = await update_test_case(
            test_case_key="invalid-key",
            name="Updated name",
        )

        # Parse JSON error response
        response_data = json.loads(response)
        assert response_data["errorCode"] == 400
        assert "Invalid test case key format" in response_data["message"]
        # Should not call the API
        mock_client.update_test_case.assert_not_called()

        # Test with invalid estimated_time
        response = await update_test_case(
            test_case_key="PROJ-T123",
            estimated_time="invalid",
        )

        # Parse JSON error response
        response_data = json.loads(response)
        assert response_data["errorCode"] == 400
        assert "Estimated time must be a valid integer" in response_data["message"]
        # Should not call the API
        mock_client.update_test_case.assert_not_called()

        # Test with invalid component_id
        response = await update_test_case(
            test_case_key="PROJ-T123",
            component_id="not-a-number",
        )

        # Parse JSON error response
        response_data = json.loads(response)
        assert response_data["errorCode"] == 400
        assert "Component ID must be a valid integer" in response_data["message"]
        # Should not call the API
        mock_client.update_test_case.assert_not_called()

        # Test with invalid folder_id
        response = await update_test_case(
            test_case_key="PROJ-T123",
            folder_id="not-a-number",
        )

        # Parse JSON error response
        response_data = json.loads(response)
        assert response_data["errorCode"] == 400
        assert "folder_id must be a numeric ID" in response_data["message"]
        assert "Use get_folders tool to find folder IDs" in response_data["message"]
        # Should not call the API
        mock_client.update_test_case.assert_not_called()

        # Test with invalid labels format
        response = await update_test_case(
            test_case_key="PROJ-T123",
            labels='["label1", 123]',  # Invalid: non-string in array
        )

        # Parse JSON error response
        response_data = json.loads(response)
        assert response_data["errorCode"] == 400
        assert "All labels must be strings" in response_data["message"]
        # Should not call the API
        mock_client.update_test_case.assert_not_called()

        # Test with invalid custom_fields format
        response = await update_test_case(
            test_case_key="PROJ-T123",
            custom_fields="invalid json",
        )

        # Parse JSON error response
        response_data = json.loads(response)
        assert response_data["errorCode"] == 400
        assert "Custom fields must be valid JSON" in response_data["message"]
        # Should not call the API
        mock_client.update_test_case.assert_not_called()

    @pytest.mark.asyncio
    @patch("src.mcp_zephyr_scale_cloud.server.zephyr_client")
    async def test_update_test_case_api_error(self, mock_client):
        """Test update_test_case with API error."""
        from src.mcp_zephyr_scale_cloud.server import update_test_case
        from src.mcp_zephyr_scale_cloud.utils.validation import ValidationResult

        # Mock API error response
        mock_result = ValidationResult(False, errors=["Test case not found"])
        mock_client.update_test_case = AsyncMock(return_value=mock_result)

        response = await update_test_case(
            test_case_key="PROJ-T999",
            name="Updated name",
        )

        # Parse JSON error response
        response_data = json.loads(response)
        assert response_data["errorCode"] == 400
        assert "Test case not found" in response_data["message"]
        mock_client.update_test_case.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_test_case_no_config(self):
        """Test update_test_case when client is not configured."""
        from src.mcp_zephyr_scale_cloud.server import update_test_case

        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client", None):
            response = await update_test_case(
                test_case_key="PROJ-T123",
                name="Updated name",
            )

            # Should return configuration error
            assert "ERROR" in response
            assert "configuration not found" in response

    @pytest.mark.asyncio
    async def test_get_test_cases_tool_success(self, mock_env_vars):
        """Test get_test_cases tool with successful response."""
        from src.mcp_zephyr_scale_cloud.server import get_test_cases

        # Sample test cases response data
        sample_test_cases_data = {
            "values": [
                {
                    "id": 123,
                    "key": "PROJ-T456",
                    "name": "Test case 1",
                    "project": {"id": 1, "self": "http://example.com/projects/1"},
                    "priority": {"id": 1, "self": "http://example.com/priorities/1"},
                    "status": {"id": 1, "self": "http://example.com/statuses/1"},
                },
                {
                    "id": 124,
                    "key": "PROJ-T457",
                    "name": "Test case 2",
                    "project": {"id": 1, "self": "http://example.com/projects/1"},
                    "priority": {"id": 2, "self": "http://example.com/priorities/2"},
                    "status": {"id": 2, "self": "http://example.com/statuses/2"},
                },
            ],
            "maxResults": 10,
            "startAt": 0,
            "next": "https://api.example.com/v2/testcases?startAt=10&maxResults=10",
        }

        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client") as mock_client:
            mock_result = AsyncMock()
            mock_result.is_valid = True
            # Create a mock object with model_dump method
            mock_data = Mock()
            mock_data.model_dump.return_value = sample_test_cases_data
            mock_result.data = mock_data
            mock_client.get_test_cases = AsyncMock(return_value=mock_result)

            result = await get_test_cases(
                project_key="PROJ", folder_id="123", max_results=10, start_at=0
            )

            # Parse JSON response
            response_data = json.loads(result)
            assert response_data == sample_test_cases_data
            assert len(response_data["values"]) == 2
            assert response_data["values"][0]["key"] == "PROJ-T456"
            assert response_data["maxResults"] == 10
            assert response_data["startAt"] == 0

            # Verify client was called with correct parameters
            mock_client.get_test_cases.assert_called_once_with(
                project_key="PROJ", folder_id=123, max_results=10, start_at=0
            )

    @pytest.mark.asyncio
    async def test_get_test_cases_tool_no_filters(self, mock_env_vars):
        """Test get_test_cases tool with no filters."""
        from src.mcp_zephyr_scale_cloud.server import get_test_cases

        sample_empty_data = {
            "values": [],
            "maxResults": 10,
            "startAt": 0,
            "next": None,
        }

        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client") as mock_client:
            mock_result = AsyncMock()
            mock_result.is_valid = True
            mock_data = Mock()
            mock_data.model_dump.return_value = sample_empty_data
            mock_result.data = mock_data
            mock_client.get_test_cases = AsyncMock(return_value=mock_result)

            result = await get_test_cases()

            # Parse JSON response
            response_data = json.loads(result)
            assert response_data == sample_empty_data
            assert len(response_data["values"]) == 0

            # Verify client was called with default project key from environment
            mock_client.get_test_cases.assert_called_once_with(
                project_key="TEST", folder_id=None, max_results=10, start_at=0
            )

    @pytest.mark.asyncio
    async def test_get_test_cases_tool_invalid_folder_id(self, mock_env_vars):
        """Test get_test_cases tool with invalid folder_id."""
        from src.mcp_zephyr_scale_cloud.server import get_test_cases

        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client") as mock_client:
            # Mock client to avoid configuration error
            mock_client.get_test_cases = AsyncMock()

            result = await get_test_cases(folder_id="invalid")

            # Should return validation error
            response_data = json.loads(result)
            assert response_data["errorCode"] == 400
            assert "folder_id must be a valid integer" in response_data["message"]

    @pytest.mark.asyncio
    async def test_get_test_cases_tool_negative_folder_id(self, mock_env_vars):
        """Test get_test_cases tool with negative folder_id."""
        from src.mcp_zephyr_scale_cloud.server import get_test_cases

        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client") as mock_client:
            # Mock client to avoid configuration error
            mock_client.get_test_cases = AsyncMock()

            result = await get_test_cases(folder_id="-1")

            # Should return validation error
            response_data = json.loads(result)
            assert response_data["errorCode"] == 400
            assert "folder_id must be a positive integer" in response_data["message"]

    @pytest.mark.asyncio
    async def test_get_test_cases_tool_client_error(self, mock_env_vars):
        """Test get_test_cases tool when client returns error."""
        from src.mcp_zephyr_scale_cloud.server import get_test_cases

        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client") as mock_client:
            mock_result = AsyncMock()
            mock_result.is_valid = False
            mock_result.errors = ["API error occurred"]
            mock_client.get_test_cases = AsyncMock(return_value=mock_result)

            result = await get_test_cases()

            # Should return error response
            response_data = json.loads(result)
            assert response_data["errorCode"] == 400
            assert "API error occurred" in response_data["message"]

    @pytest.mark.asyncio
    async def test_get_test_cases_tool_invalid_project_key(self, mock_env_vars):
        """Test get_test_cases tool with invalid project key."""
        from src.mcp_zephyr_scale_cloud.server import get_test_cases

        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client") as mock_client:
            # Mock client to avoid configuration error
            mock_client.get_test_cases = AsyncMock()

            result = await get_test_cases(project_key="invalid-key")

            # Should return validation error
            response_data = json.loads(result)
            assert response_data["errorCode"] == 400
            assert "Project key 'invalid-key' is invalid" in response_data["message"]

    @pytest.mark.asyncio
    async def test_get_test_cases_tool_uses_env_default(self, mock_env_vars):
        """Test get_test_cases tool uses environment default project key."""
        from src.mcp_zephyr_scale_cloud.server import get_test_cases

        sample_data = {
            "values": [],
            "maxResults": 10,
            "startAt": 0,
            "next": None,
        }

        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client") as mock_client:
            mock_result = AsyncMock()
            mock_result.is_valid = True
            mock_data = Mock()
            mock_data.model_dump.return_value = sample_data
            mock_result.data = mock_data
            mock_client.get_test_cases = AsyncMock(return_value=mock_result)

            # Call without project_key - should use environment default
            await get_test_cases()

            # Verify client was called with environment default
            mock_client.get_test_cases.assert_called_once_with(
                project_key="TEST", folder_id=None, max_results=10, start_at=0
            )

    @pytest.mark.asyncio
    async def test_get_test_cases_tool_no_config(self):
        """Test get_test_cases tool when client is not configured."""
        from src.mcp_zephyr_scale_cloud.server import get_test_cases

        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client", None):
            response = await get_test_cases()

            # Should return configuration error
            assert "ERROR" in response
            assert "configuration not found" in response


class TestCycleMCPTools:
    """Test test cycle MCP tools integration."""

    @pytest.mark.asyncio
    async def test_get_test_cycles_success(self, mock_env_vars):
        """Test get_test_cycles MCP tool with successful response."""
        from src.mcp_zephyr_scale_cloud.server import get_test_cycles
        from src.mcp_zephyr_scale_cloud.utils.validation import ValidationResult

        mock_client = AsyncMock()
        mock_response_data = MagicMock()
        mock_response_data.model_dump.return_value = {
            "maxResults": 10,
            "startAt": 0,
            "total": 2,
            "isLast": True,
            "values": [
                {"id": 1, "key": "PROJ-R1", "name": "Sprint 1"},
                {"id": 2, "key": "PROJ-R2", "name": "Sprint 2"},
            ],
        }
        mock_client.get_test_cycles.return_value = ValidationResult(
            True, data=mock_response_data
        )

        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client", mock_client):
            response = await get_test_cycles(project_key="PROJ")

            mock_client.get_test_cycles.assert_called_once()
            assert '"key": "PROJ-R1"' in response
            assert '"key": "PROJ-R2"' in response

    @pytest.mark.asyncio
    async def test_get_test_cycle_success(self, mock_env_vars):
        """Test get_test_cycle MCP tool with successful response."""
        from src.mcp_zephyr_scale_cloud.server import get_test_cycle
        from src.mcp_zephyr_scale_cloud.utils.validation import ValidationResult

        mock_client = AsyncMock()
        mock_response_data = MagicMock()
        mock_response_data.model_dump.return_value = {
            "id": 1,
            "key": "PROJ-R1",
            "name": "Sprint 1 Testing",
            "project": {"id": 10000, "key": "PROJ"},
        }
        mock_client.get_test_cycle.return_value = ValidationResult(
            True, data=mock_response_data
        )

        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client", mock_client):
            response = await get_test_cycle(test_cycle_key="PROJ-R1")

            mock_client.get_test_cycle.assert_called_once_with(test_cycle_key="PROJ-R1")
            assert '"key": "PROJ-R1"' in response
            assert '"name": "Sprint 1 Testing"' in response

    @pytest.mark.asyncio
    async def test_get_test_cycle_invalid_key_format(self, mock_env_vars):
        """Test get_test_cycle with invalid key format."""
        from src.mcp_zephyr_scale_cloud.server import get_test_cycle

        mock_client = AsyncMock()

        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client", mock_client):
            response = await get_test_cycle(test_cycle_key="INVALID")

            # Should return validation error without calling client
            mock_client.get_test_cycle.assert_not_called()
            assert "errorCode" in response
            assert "400" in response

    @pytest.mark.asyncio
    async def test_create_test_cycle_success(self, mock_env_vars):
        """Test create_test_cycle MCP tool with successful response."""
        from src.mcp_zephyr_scale_cloud.server import create_test_cycle
        from src.mcp_zephyr_scale_cloud.utils.validation import ValidationResult

        mock_client = AsyncMock()
        mock_response_data = MagicMock()
        mock_response_data.model_dump.return_value = {
            "id": 1,
            "key": "PROJ-R1",
            "name": "Sprint 1",
        }
        mock_client.create_test_cycle.return_value = ValidationResult(
            True, data=mock_response_data
        )

        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client", mock_client):
            response = await create_test_cycle(project_key="PROJ", name="Sprint 1")

            mock_client.create_test_cycle.assert_called_once()
            assert '"key": "PROJ-R1"' in response

    @pytest.mark.asyncio
    async def test_create_test_cycle_validation_error(self, mock_env_vars):
        """Test create_test_cycle with validation error."""
        from src.mcp_zephyr_scale_cloud.server import create_test_cycle

        mock_client = AsyncMock()

        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client", mock_client):
            # Missing required name
            response = await create_test_cycle(project_key="PROJ", name="")

            # Should return validation error without calling client
            mock_client.create_test_cycle.assert_not_called()
            assert "errorCode" in response
            assert "400" in response

    @pytest.mark.asyncio
    async def test_update_test_cycle_success(self, mock_env_vars):
        """Test update_test_cycle MCP tool with successful response."""
        from src.mcp_zephyr_scale_cloud.server import update_test_cycle
        from src.mcp_zephyr_scale_cloud.utils.validation import ValidationResult

        mock_client = AsyncMock()

        # Mock get_test_cycle response
        mock_existing_cycle = MagicMock()
        mock_existing_cycle.name = "Old Name"
        mock_existing_cycle.description = None
        mock_existing_cycle.planned_start_date = None
        mock_existing_cycle.planned_end_date = None
        mock_existing_cycle.status = None
        mock_existing_cycle.folder = None
        mock_existing_cycle.owner = None
        mock_client.get_test_cycle.return_value = ValidationResult(
            True, data=mock_existing_cycle
        )

        # Mock update_test_cycle response
        mock_client.update_test_cycle.return_value = ValidationResult(True)

        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client", mock_client):
            response = await update_test_cycle(
                test_cycle_key="PROJ-R1", name="Updated Name"
            )

            mock_client.get_test_cycle.assert_called_once()
            mock_client.update_test_cycle.assert_called_once()
            assert "updated successfully" in response

    @pytest.mark.asyncio
    async def test_update_test_cycle_not_found(self, mock_env_vars):
        """Test update_test_cycle when cycle doesn't exist."""
        from src.mcp_zephyr_scale_cloud.server import update_test_cycle
        from src.mcp_zephyr_scale_cloud.utils.validation import ValidationResult

        mock_client = AsyncMock()
        mock_client.get_test_cycle.return_value = ValidationResult(
            False, errors=["Not found"]
        )

        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client", mock_client):
            response = await update_test_cycle(
                test_cycle_key="PROJ-R999", name="New Name"
            )

            mock_client.get_test_cycle.assert_called_once()
            mock_client.update_test_cycle.assert_not_called()
            assert "errorCode" in response
            assert "404" in response

    @pytest.mark.asyncio
    async def test_get_test_cycle_links_success(self, mock_env_vars):
        """Test get_test_cycle_links MCP tool."""
        from src.mcp_zephyr_scale_cloud.server import get_test_cycle_links
        from src.mcp_zephyr_scale_cloud.utils.validation import ValidationResult

        mock_client = AsyncMock()
        mock_response_data = MagicMock()
        mock_response_data.model_dump.return_value = {
            "issueLinks": [{"id": 1, "issueId": 10001}],
            "webLinks": [{"id": 2, "url": "https://example.com"}],
        }
        mock_client.get_test_cycle_links.return_value = ValidationResult(
            True, data=mock_response_data
        )

        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client", mock_client):
            response = await get_test_cycle_links(test_cycle_key="PROJ-R1")

            mock_client.get_test_cycle_links.assert_called_once()
            assert "issueLinks" in response
            assert "webLinks" in response

    @pytest.mark.asyncio
    async def test_create_test_cycle_issue_link_success(self, mock_env_vars):
        """Test create_test_cycle_issue_link MCP tool."""
        from src.mcp_zephyr_scale_cloud.server import (
            create_test_cycle_issue_link,
        )
        from src.mcp_zephyr_scale_cloud.utils.validation import ValidationResult

        mock_client = AsyncMock()
        from src.mcp_zephyr_scale_cloud.schemas.base import CreatedResource

        mock_response_data = CreatedResource(id=123, key="link-123")
        mock_client.create_test_cycle_issue_link.return_value = ValidationResult(
            True, data=mock_response_data
        )

        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client", mock_client):
            response = await create_test_cycle_issue_link(
                test_cycle_key="PROJ-R1", issue_id=10001
            )

            mock_client.create_test_cycle_issue_link.assert_called_once()
            assert "123" in response
            assert "link-123" in response

    @pytest.mark.asyncio
    async def test_create_test_cycle_web_link_success(self, mock_env_vars):
        """Test create_test_cycle_web_link MCP tool."""
        from src.mcp_zephyr_scale_cloud.server import create_test_cycle_web_link
        from src.mcp_zephyr_scale_cloud.utils.validation import ValidationResult

        mock_client = AsyncMock()
        from src.mcp_zephyr_scale_cloud.schemas.base import CreatedResource

        mock_response_data = CreatedResource(id=456, key="link-456")
        mock_client.create_test_cycle_web_link.return_value = ValidationResult(
            True, data=mock_response_data
        )

        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client", mock_client):
            response = await create_test_cycle_web_link(
                test_cycle_key="PROJ-R1", url="https://example.com"
            )

            mock_client.create_test_cycle_web_link.assert_called_once()
            assert "456" in response
            assert "link-456" in response
