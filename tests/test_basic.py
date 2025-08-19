"""Basic integration tests for the MCP server."""

import os

import pytest

from src.mcp_zephyr_scale_cloud.config import ZephyrConfig
from src.mcp_zephyr_scale_cloud.schemas.priority import CreatePriorityRequest
from src.mcp_zephyr_scale_cloud.server import mcp
from src.mcp_zephyr_scale_cloud.utils.validation import (
    ValidationResult,
    validate_pagination_params,
    validate_project_key,
)


class TestBasicFunctionality:
    """Basic functionality tests."""

    def test_config_creation(self):
        """Test creating config with valid data."""
        config = ZephyrConfig(
            api_token="test_token",
            base_url="https://api.example.com/v2",
            project_key="TEST",
        )

        assert config.api_token == "test_token"
        assert config.base_url == "https://api.example.com/v2"
        assert config.project_key == "TEST"

    def test_priority_schema_creation(self):
        """Test creating priority request schema."""
        request = CreatePriorityRequest(
            projectKey="TEST",
            name="High Priority",
            description="Test description",
            color="#FF0000",
        )

        assert request.projectKey == "TEST"
        assert request.name == "High Priority"
        assert request.description == "Test description"
        assert request.color == "#FF0000"

    def test_priority_schema_validation(self):
        """Test priority schema validation."""
        # Test invalid project key
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            CreatePriorityRequest(
                projectKey="invalid-key", name="Priority"  # Should be uppercase
            )

    def test_validation_result(self):
        """Test ValidationResult class."""
        # Success case
        success = ValidationResult(True, data={"key": "value"})
        assert success.is_valid
        assert success.data == {"key": "value"}
        assert success.errors == []

        # Failure case
        failure = ValidationResult(False, ["Error message"])
        assert not failure.is_valid
        assert failure.errors == ["Error message"]
        assert failure.data is None

    def test_project_key_validation(self):
        """Test project key validation."""
        # Valid cases
        result = validate_project_key("TEST")
        assert result.is_valid
        assert result.data == "TEST"

        result = validate_project_key("PROJ123")
        assert result.is_valid

        # Invalid cases
        result = validate_project_key("test")  # lowercase
        assert not result.is_valid

        result = validate_project_key("TEST-123")  # special chars
        assert not result.is_valid

        result = validate_project_key("")  # empty
        assert not result.is_valid

    def test_pagination_validation(self):
        """Test pagination parameter validation."""
        # Valid cases
        result = validate_pagination_params(max_results=10, start_at=0)
        assert result.is_valid
        assert result.data["maxResults"] == 10
        assert result.data["startAt"] == 0

        # Default values
        result = validate_pagination_params()
        assert result.is_valid
        assert result.data["maxResults"] == 50
        assert result.data["startAt"] == 0

        # Invalid cases
        result = validate_pagination_params(max_results=2000)  # too high
        assert not result.is_valid

        result = validate_pagination_params(max_results=0)  # too low
        assert not result.is_valid

        result = validate_pagination_params(start_at=-1)  # negative
        assert not result.is_valid

    @pytest.mark.asyncio
    async def test_mcp_server_tools(self):
        """Test MCP server has expected tools."""
        tools = await mcp.list_tools()

        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "healthcheck",
            "get_priorities",
            "get_priority",
            "create_priority",
            "update_priority",
        ]

        for tool_name in expected_tools:
            assert tool_name in tool_names, f"Tool {tool_name} not found"

    def test_model_dump_camelcase(self):
        """Test that Pydantic models use camelCase in output."""
        request = CreatePriorityRequest(projectKey="TEST", name="Priority")

        dumped = request.model_dump(exclude_none=True)

        # Should have camelCase key due to alias
        assert "projectKey" in dumped
        assert dumped["projectKey"] == "TEST"
        assert dumped["name"] == "Priority"


class TestEnvironmentConfiguration:
    """Test environment-based configuration."""

    def test_config_from_env_with_test_vars(self):
        """Test config creation from test environment variables."""
        # Save original environment
        original_env = os.environ.copy()

        try:
            # Set test environment variables
            os.environ["ZEPHYR_SCALE_API_TOKEN"] = "test_token_123"
            os.environ["ZEPHYR_SCALE_BASE_URL"] = "https://api.example.com/v2"
            os.environ["ZEPHYR_SCALE_DEFAULT_PROJECT_KEY"] = "TEST"

            config = ZephyrConfig.from_env()

            assert config.api_token == "test_token_123"
            assert config.base_url == "https://api.example.com/v2"
            assert config.project_key == "TEST"

        finally:
            # Restore original environment
            os.environ.clear()
            os.environ.update(original_env)

    def test_config_missing_token_error(self):
        """Test config creation fails when API token is missing."""
        # Save original environment
        original_env = os.environ.copy()

        try:
            # Clear API token
            if "ZEPHYR_SCALE_API_TOKEN" in os.environ:
                del os.environ["ZEPHYR_SCALE_API_TOKEN"]

            with pytest.raises(
                ValueError,
                match="ZEPHYR_SCALE_API_TOKEN environment variable is required",
            ):
                ZephyrConfig.from_env()

        finally:
            # Restore original environment
            os.environ.clear()
            os.environ.update(original_env)
