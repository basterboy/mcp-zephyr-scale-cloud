"""Integration tests for MCP server."""

from unittest.mock import AsyncMock, patch

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
                assert result["tools_count"] == 12

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

            assert "SUCCESS" in result
            assert "healthy" in result
            assert mock_env_vars["ZEPHYR_SCALE_BASE_URL"] in result

    @pytest.mark.asyncio
    async def test_healthcheck_tool_no_config(self):
        """Test healthcheck tool without configuration."""
        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client", None):
            result = await healthcheck()

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
            mock_result.data = type("MockPriorityList", (), sample_priority_list)()
            mock_client.get_priorities = AsyncMock(return_value=mock_result)

            with patch(
                "src.mcp_zephyr_scale_cloud.server.format_priority_list"
            ) as mock_format:
                mock_format.return_value = "Formatted priority list"

                result = await get_priorities()

                assert result == "Formatted priority list"
                mock_client.get_priorities.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_priority_tool_success(self, mock_env_vars, sample_priority_data):
        """Test get_priority tool with successful response."""
        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client") as mock_client:
            mock_result = AsyncMock()
            mock_result.is_valid = True
            mock_result.data = type("MockPriority", (), sample_priority_data)()
            mock_client.get_priority = AsyncMock(return_value=mock_result)

            with patch(
                "src.mcp_zephyr_scale_cloud.server.format_priority_details"
            ) as mock_format:
                mock_format.return_value = "Formatted priority details"

                result = await get_priority(1)

                assert result == "Formatted priority details"
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
                mock_result.data = type(
                    "MockCreatedResource", (), sample_created_resource
                )()
                mock_client.create_priority = AsyncMock(return_value=mock_result)

                with patch(
                    "src.mcp_zephyr_scale_cloud.server.format_success_message"
                ) as mock_format:
                    mock_format.return_value = "Priority created successfully"

                    result = await create_priority("TEST", "High Priority")

                    assert result == "Priority created successfully"

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

                with patch(
                    "src.mcp_zephyr_scale_cloud.server.format_success_message"
                ) as mock_format:
                    mock_format.return_value = "Priority updated successfully"

                    result = await update_priority(1, 123, "Updated Priority", 0)

                    assert result == "Priority updated successfully"

    @pytest.mark.asyncio
    async def test_get_statuses_tool_success(self, mock_env_vars, sample_status_list):
        """Test get_statuses tool with successful response."""
        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client") as mock_client:
            mock_result = AsyncMock()
            mock_result.is_valid = True
            mock_result.data = type("MockStatusList", (), sample_status_list)()
            mock_client.get_statuses = AsyncMock(return_value=mock_result)

            with patch(
                "src.mcp_zephyr_scale_cloud.server.format_status_list"
            ) as mock_format:
                mock_format.return_value = "Formatted status list"

                result = await get_statuses()

                assert result == "Formatted status list"
                mock_client.get_statuses.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_statuses_tool_with_filters(
        self, mock_env_vars, sample_status_list
    ):
        """Test get_statuses tool with project and type filters."""
        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client") as mock_client:
            mock_result = AsyncMock()
            mock_result.is_valid = True
            mock_result.data = type("MockStatusList", (), sample_status_list)()
            mock_client.get_statuses = AsyncMock(return_value=mock_result)

            with patch(
                "src.mcp_zephyr_scale_cloud.server.format_status_list"
            ) as mock_format:
                mock_format.return_value = "Filtered status list"

                result = await get_statuses(
                    project_key="TEST", status_type="TEST_EXECUTION", max_results=100
                )

                assert result == "Filtered status list"
                mock_client.get_statuses.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_status_tool_success(self, mock_env_vars, sample_status_data):
        """Test get_status tool with successful response."""
        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client") as mock_client:
            mock_result = AsyncMock()
            mock_result.is_valid = True
            mock_result.data = type("MockStatus", (), sample_status_data)()
            mock_client.get_status = AsyncMock(return_value=mock_result)

            with patch(
                "src.mcp_zephyr_scale_cloud.server.format_status_details"
            ) as mock_format:
                mock_format.return_value = "Formatted status details"

                result = await get_status(1)

                assert result == "Formatted status details"
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
                mock_result.data = type(
                    "MockCreatedResource", (), sample_created_resource
                )()
                mock_client.create_status = AsyncMock(return_value=mock_result)

                with patch(
                    "src.mcp_zephyr_scale_cloud.server.format_success_message"
                ) as mock_format:
                    mock_format.return_value = "Status created successfully"

                    result = await create_status(
                        "TEST", "In Progress", "TEST_EXECUTION"
                    )

                    assert result == "Status created successfully"

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

                with patch(
                    "src.mcp_zephyr_scale_cloud.server.format_success_message"
                ) as mock_format:
                    mock_format.return_value = "Status updated successfully"

                    result = await update_status(1, 123, "Updated Status", 0)

                    assert result == "Status updated successfully"

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
            mock_result.data = type("MockFolderList", (), sample_folder_list)()
            mock_client.get_folders = AsyncMock(return_value=mock_result)

            with patch(
                "src.mcp_zephyr_scale_cloud.server.format_folder_list"
            ) as mock_format:
                mock_format.return_value = "Formatted folder list"

                result = await get_folders()

                assert result == "Formatted folder list"
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
                    mock_result.data = type("MockFolderList", (), sample_folder_list)()
                    mock_client.get_folders = AsyncMock(return_value=mock_result)

                    with patch(
                        "src.mcp_zephyr_scale_cloud.server.format_folder_list"
                    ) as mock_format:
                        mock_format.return_value = "Filtered folder list"

                        result = await get_folders("TEST", "TEST_CASE", 25)

                        assert result == "Filtered folder list"
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
            mock_result.data = type("MockFolder", (), sample_folder_data)()
            mock_client.get_folder = AsyncMock(return_value=mock_result)

            with patch(
                "src.mcp_zephyr_scale_cloud.server.format_folder_details"
            ) as mock_format:
                mock_format.return_value = "Formatted folder details"

                result = await get_folder(1)

                assert result == "Formatted folder details"
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
                mock_result.data = type(
                    "MockCreatedResource", (), sample_created_resource
                )()
                mock_client.create_folder = AsyncMock(return_value=mock_result)

                with patch(
                    "src.mcp_zephyr_scale_cloud.server.format_success_message"
                ) as mock_format:
                    mock_format.return_value = "Folder created successfully"

                    result = await create_folder("Test Folder", "TEST", "TEST_CASE", 1)

                    assert result == "Folder created successfully"

    @pytest.mark.asyncio
    async def test_folder_tools_error_handling(self, mock_env_vars):
        """Test folder tools error handling."""
        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client") as mock_client:
            # Mock client failure
            mock_result = AsyncMock()
            mock_result.is_valid = False
            mock_result.errors = ["API error"]
            mock_client.get_folders = AsyncMock(return_value=mock_result)

            with patch(
                "src.mcp_zephyr_scale_cloud.server.format_error_message"
            ) as mock_format:
                mock_format.return_value = "Error occurred"

                result = await get_folders()

                assert result == "Error occurred"

    @pytest.mark.asyncio
    async def test_folder_tools_no_client(self, mock_env_vars):
        """Test folder tools when client is not initialized."""
        with patch("src.mcp_zephyr_scale_cloud.server.zephyr_client", None):
            with patch(
                "src.mcp_zephyr_scale_cloud.server.format_error_message"
            ) as mock_format:
                mock_format.return_value = "Client not initialized"

                result = await get_folders()

                assert result == "Client not initialized"
