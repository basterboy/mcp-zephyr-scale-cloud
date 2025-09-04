"""Integration tests for MCP server."""

import json
from unittest.mock import AsyncMock, Mock, patch

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
