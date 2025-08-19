"""Tests for validation utilities."""

from src.mcp_zephyr_scale_cloud.schemas.priority import Priority
from src.mcp_zephyr_scale_cloud.utils.validation import (
    ValidationResult,
    sanitize_input,
    validate_api_response,
    validate_pagination_params,
    validate_priority_data,
    validate_project_key,
)


class TestValidationResult:
    """Test cases for ValidationResult."""

    def test_validation_result_success(self):
        """Test successful ValidationResult."""
        result = ValidationResult(True, data={"key": "value"})

        assert result.is_valid is True
        assert result.errors == []
        assert result.data == {"key": "value"}

    def test_validation_result_failure(self):
        """Test failed ValidationResult."""
        result = ValidationResult(False, ["Error 1", "Error 2"])

        assert result.is_valid is False
        assert result.errors == ["Error 1", "Error 2"]
        assert result.data is None

    def test_validation_result_bool_conversion(self):
        """Test ValidationResult boolean conversion."""
        success = ValidationResult(True)
        failure = ValidationResult(False, ["Error"])

        assert bool(success) is True
        assert bool(failure) is False


class TestPriorityValidation:
    """Test cases for priority data validation."""

    def test_validate_priority_create_success(self):
        """Test successful priority creation validation."""
        data = {
            "projectKey": "TEST",
            "name": "High Priority",
            "description": "Test description",
            "color": "#FF0000",
        }

        result = validate_priority_data(data, is_update=False)

        assert result.is_valid
        assert result.data.projectKey == "TEST"
        assert result.data.name == "High Priority"

    def test_validate_priority_update_success(self):
        """Test successful priority update validation."""
        data = {
            "id": 1,
            "project": {"id": 123},
            "name": "Updated Priority",
            "index": 0,
            "default": False,
            "description": "Updated description",
            "color": "#00FF00",
        }

        result = validate_priority_data(data, is_update=True)

        assert result.is_valid
        assert result.data.id == 1
        assert result.data.name == "Updated Priority"

    def test_validate_priority_create_invalid(self):
        """Test failed priority creation validation."""
        data = {
            "projectKey": "invalid-key",  # Invalid format
            "name": "",  # Empty name
        }

        result = validate_priority_data(data, is_update=False)

        assert not result.is_valid
        assert len(result.errors) > 0
        assert any("projectKey" in error or "name" in error for error in result.errors)

    def test_validate_priority_missing_required(self):
        """Test validation with missing required fields."""
        data = {}  # Missing required fields

        result = validate_priority_data(data, is_update=False)

        assert not result.is_valid
        assert len(result.errors) > 0


class TestProjectKeyValidation:
    """Test cases for project key validation."""

    def test_validate_project_key_valid(self):
        """Test valid project key validation."""
        result = validate_project_key("TEST")

        assert result.is_valid
        assert result.data == "TEST"

    def test_validate_project_key_valid_with_numbers(self):
        """Test valid project key with numbers."""
        result = validate_project_key("PROJ123")

        assert result.is_valid
        assert result.data == "PROJ123"

    def test_validate_project_key_invalid_lowercase(self):
        """Test invalid project key (lowercase)."""
        result = validate_project_key("test")

        assert not result.is_valid
        assert "uppercase letters" in result.errors[0]

    def test_validate_project_key_invalid_special_chars(self):
        """Test invalid project key (special characters)."""
        result = validate_project_key("TEST-123")

        assert not result.is_valid
        assert "letters, numbers, and underscores" in result.errors[0]

    def test_validate_project_key_empty(self):
        """Test empty project key."""
        result = validate_project_key("")

        assert not result.is_valid
        assert "required" in result.errors[0]


class TestPaginationValidation:
    """Test cases for pagination parameter validation."""

    def test_validate_pagination_valid(self):
        """Test valid pagination parameters."""
        result = validate_pagination_params(max_results=10, start_at=0)

        assert result.is_valid
        assert result.data["maxResults"] == 10
        assert result.data["startAt"] == 0

    def test_validate_pagination_defaults(self):
        """Test pagination with default values."""
        result = validate_pagination_params()

        assert result.is_valid
        assert result.data["maxResults"] == 50
        assert result.data["startAt"] == 0

    def test_validate_pagination_max_results_too_high(self):
        """Test pagination with max_results too high."""
        result = validate_pagination_params(max_results=2000)

        assert not result.is_valid
        assert "cannot exceed 1000" in result.errors[0]

    def test_validate_pagination_max_results_too_low(self):
        """Test pagination with max_results too low."""
        result = validate_pagination_params(max_results=0)

        assert not result.is_valid
        assert "must be at least 1" in result.errors[0]

    def test_validate_pagination_start_at_negative(self):
        """Test pagination with negative start_at."""
        result = validate_pagination_params(start_at=-1)

        assert not result.is_valid
        assert "must be non-negative" in result.errors[0]


class TestApiResponseValidation:
    """Test cases for API response validation."""

    def test_validate_api_response_success(self, sample_priority_data):
        """Test successful API response validation."""
        result = validate_api_response(sample_priority_data, Priority)

        assert result.is_valid
        assert isinstance(result.data, Priority)
        assert result.data.id == 1

    def test_validate_api_response_invalid_data(self):
        """Test API response validation with invalid data."""
        invalid_data = {"invalid": "data"}

        result = validate_api_response(invalid_data, Priority)

        assert not result.is_valid
        assert len(result.errors) > 0

    def test_validate_api_response_exception(self):
        """Test API response validation with exception."""
        # Pass non-dict data to cause an exception
        result = validate_api_response("invalid", Priority)

        assert not result.is_valid
        assert len(result.errors) > 0


class TestInputSanitization:
    """Test cases for input sanitization."""

    def test_sanitize_input_basic(self):
        """Test basic input sanitization."""
        result = sanitize_input("  Hello World  ")
        assert result == "Hello World"

    def test_sanitize_input_none(self):
        """Test sanitizing None input."""
        result = sanitize_input(None)
        assert result is None

    def test_sanitize_input_empty(self):
        """Test sanitizing empty string."""
        result = sanitize_input("")
        assert result == ""

    def test_sanitize_input_with_special_chars(self):
        """Test sanitizing input with special characters."""
        result = sanitize_input("  Test@123!  ")
        assert result == "Test@123!"
