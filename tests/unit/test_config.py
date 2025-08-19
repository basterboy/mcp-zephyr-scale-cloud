"""Tests for configuration management."""

import os

import pytest

from src.mcp_zephyr_scale_cloud.config import ZephyrConfig


class TestZephyrConfig:
    """Test cases for ZephyrConfig."""

    def test_config_from_env_valid(self, mock_env_vars):
        """Test creating config from valid environment variables."""
        config = ZephyrConfig.from_env()

        assert config.api_token == "test_token_123"
        assert config.base_url == "https://api.example.com/v2"
        assert config.project_key == "TEST"

    def test_config_from_env_missing_token(self):
        """Test creating config when API token is missing."""
        # Clear the token
        if "ZEPHYR_SCALE_API_TOKEN" in os.environ:
            del os.environ["ZEPHYR_SCALE_API_TOKEN"]

        with pytest.raises(
            ValueError, match="ZEPHYR_SCALE_API_TOKEN environment variable is required"
        ):
            ZephyrConfig.from_env()

    def test_config_default_values(self, mock_env_vars):
        """Test config uses default values when optional vars are missing."""
        # Remove optional variables
        if "ZEPHYR_SCALE_BASE_URL" in os.environ:
            del os.environ["ZEPHYR_SCALE_BASE_URL"]
        if "ZEPHYR_SCALE_DEFAULT_PROJECT_KEY" in os.environ:
            del os.environ["ZEPHYR_SCALE_DEFAULT_PROJECT_KEY"]

        config = ZephyrConfig.from_env()

        assert config.api_token == "test_token_123"
        assert config.base_url == "https://api.zephyrscale.smartbear.com/v2"  # Default
        assert config.project_key is None  # Default

    def test_config_direct_creation(self):
        """Test creating config directly with parameters."""
        config = ZephyrConfig(
            api_token="direct_token",
            base_url="https://custom.api.com/v2",
            project_key="CUSTOM",
        )

        assert config.api_token == "direct_token"
        assert config.base_url == "https://custom.api.com/v2"
        assert config.project_key == "CUSTOM"

    def test_config_validation(self):
        """Test config validation with invalid data."""
        # Test that we can create config with minimal valid data
        config = ZephyrConfig(api_token="test_token")
        assert config.api_token == "test_token"
        assert config.base_url == "https://api.zephyrscale.smartbear.com/v2"  # default
