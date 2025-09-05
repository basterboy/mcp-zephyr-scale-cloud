"""Tests for validation utilities."""

from src.mcp_zephyr_scale_cloud.schemas.priority import Priority
from src.mcp_zephyr_scale_cloud.utils.validation import (
    ValidationResult,
    sanitize_input,
    validate_api_response,
    validate_folder_data,
    validate_folder_type,
    validate_pagination_params,
    validate_priority_data,
    validate_project_key,
    validate_status_data,
    validate_status_type,
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
        assert "No project key provided" in result.errors[0]


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


class TestStatusValidation:
    """Test cases for status validation functions."""

    def test_validate_status_create_success(self):
        """Test successful status data validation for creation."""
        data = {
            "project_key": "TEST",
            "name": "In Progress",
            "type": "TEST_EXECUTION",
            "description": "Test in progress",
            "color": "#FFA500",
        }

        result = validate_status_data(data, is_update=False)

        assert result.is_valid
        assert result.data.project_key == "TEST"
        assert result.data.name == "In Progress"
        assert result.data.type.value == "TEST_EXECUTION"
        assert result.data.description == "Test in progress"
        assert result.data.color == "#FFA500"

    def test_validate_status_update_success(self):
        """Test successful status data validation for update."""
        data = {
            "id": 123,
            "project": {"id": 456},
            "name": "Updated Status",
            "index": 5,
            "default": False,
            "archived": False,
            "description": "Updated description",
            "color": "#00FF00",
        }

        result = validate_status_data(data, is_update=True)

        assert result.is_valid
        assert result.data.id == 123
        assert result.data.project.id == 456
        assert result.data.name == "Updated Status"
        assert result.data.index == 5
        assert result.data.default is False
        assert result.data.archived is False

    def test_validate_status_create_invalid(self):
        """Test status data validation with invalid data."""
        data = {
            "project_key": "invalid-key",  # Invalid format
            "name": "",  # Empty name
            "type": "INVALID_TYPE",  # Invalid status type
            "color": "invalid-color",  # Invalid color format
        }

        result = validate_status_data(data, is_update=False)

        assert not result.is_valid
        assert len(result.errors) > 0

    def test_validate_status_missing_required(self):
        """Test status data validation with missing required fields."""
        data = {"name": "Status"}  # Missing project_key and type

        result = validate_status_data(data, is_update=False)

        assert not result.is_valid
        assert len(result.errors) > 0

    def test_validate_status_update_missing_fields(self):
        """Test status update validation with missing fields."""
        data = {"name": "Status"}  # Missing id, project, index, archived, default

        result = validate_status_data(data, is_update=True)

        assert not result.is_valid
        assert len(result.errors) > 0


class TestStatusTypeValidation:
    """Test cases for status type validation."""

    def test_validate_status_type_valid(self):
        """Test valid status type validation."""
        for status_type in ["TEST_CASE", "TEST_PLAN", "TEST_CYCLE", "TEST_EXECUTION"]:
            result = validate_status_type(status_type)
            assert result.is_valid
            assert result.data.value == status_type

    def test_validate_status_type_invalid(self):
        """Test invalid status type validation."""
        result = validate_status_type("INVALID_TYPE")

        assert not result.is_valid
        assert "Invalid status type" in result.errors[0]
        assert "INVALID_TYPE" in result.errors[0]

    def test_validate_status_type_empty(self):
        """Test empty status type validation."""
        result = validate_status_type("")

        assert not result.is_valid
        assert "Invalid status type" in result.errors[0]

    def test_validate_status_type_none(self):
        """Test None status type validation."""
        result = validate_status_type(None)

        assert not result.is_valid
        assert "Invalid status type" in result.errors[0]

    def test_validate_status_type_case_sensitive(self):
        """Test that status type validation is case sensitive."""
        result = validate_status_type("test_execution")  # lowercase

        assert not result.is_valid
        assert "Invalid status type" in result.errors[0]


class TestFolderValidation:
    """Test cases for folder validation."""

    def test_validate_folder_create_success(self):
        """Test successful folder creation validation."""
        data = {
            "name": "Test Folder",
            "project_key": "TEST",
            "folder_type": "TEST_CASE",
            "parent_id": 1,
        }

        result = validate_folder_data(data)

        assert result.is_valid
        assert result.data.name == "Test Folder"
        assert result.data.project_key == "TEST"
        assert result.data.folder_type.value == "TEST_CASE"
        assert result.data.parent_id == 1

    def test_validate_folder_create_minimal(self):
        """Test folder creation validation with minimal data (root folder)."""
        data = {
            "name": "Root Folder",
            "project_key": "TEST",
            "folder_type": "TEST_PLAN",
        }

        result = validate_folder_data(data)

        assert result.is_valid
        assert result.data.name == "Root Folder"
        assert result.data.project_key == "TEST"
        assert result.data.folder_type.value == "TEST_PLAN"
        assert result.data.parent_id is None

    def test_validate_folder_create_invalid(self):
        """Test folder creation validation with invalid data."""
        data = {
            "name": "",  # Empty name
            "project_key": "invalid",  # Invalid project key
            "folder_type": "INVALID_TYPE",  # Invalid folder type
        }

        result = validate_folder_data(data)

        assert not result.is_valid
        assert len(result.errors) > 0

    def test_validate_folder_missing_required(self):
        """Test folder validation with missing required fields."""
        data = {"name": "Folder"}  # Missing project_key and folder_type

        result = validate_folder_data(data)

        assert not result.is_valid
        assert len(result.errors) > 0


class TestFolderTypeValidation:
    """Test cases for folder type validation."""

    def test_validate_folder_type_valid(self):
        """Test valid folder type validation."""
        for folder_type in ["TEST_CASE", "TEST_PLAN", "TEST_CYCLE"]:
            result = validate_folder_type(folder_type)
            assert result.is_valid
            assert result.data.value == folder_type

    def test_validate_folder_type_invalid(self):
        """Test invalid folder type validation."""
        result = validate_folder_type("INVALID_TYPE")

        assert not result.is_valid
        assert "Invalid folder type" in result.errors[0]
        assert "INVALID_TYPE" in result.errors[0]

    def test_validate_folder_type_empty(self):
        """Test empty folder type validation."""
        result = validate_folder_type("")

        assert not result.is_valid
        assert "Invalid folder type" in result.errors[0]

    def test_validate_folder_type_none(self):
        """Test None folder type validation."""
        result = validate_folder_type(None)

        assert not result.is_valid
        assert "Invalid folder type" in result.errors[0]

    def test_validate_folder_type_case_sensitive(self):
        """Test that folder type validation is case sensitive."""
        result = validate_folder_type("test_case")  # lowercase

        assert not result.is_valid
        assert "Invalid folder type" in result.errors[0]


class TestTestCaseUpdateInputValidation:
    """Test cases for test case update input validation."""

    def test_validate_test_case_update_input_valid_all_fields(self):
        """Test valid test case update input with all fields."""
        from src.mcp_zephyr_scale_cloud.utils.validation import (
            validate_test_case_update_input,
        )

        data = {
            "name": "Updated test case",
            "objective": "Updated objective",
            "precondition": "Updated precondition",
            "estimatedTime": 120000,
            "component": {"id": 123},
            "priority": {"id": 456},
            "status": {"id": 789},
            "folderId": 456,
            "ownerId": "user123",
            "labels": ["automation", "regression"],
            "customFields": {"Component": "Test", "Version": "v2.0"},
        }

        result = validate_test_case_update_input(data)

        assert result.is_valid
        assert result.data.name == "Updated test case"
        assert result.data.objective == "Updated objective"
        assert result.data.estimated_time == 120000
        assert result.data.component == {"id": 123}
        assert result.data.priority == {"id": 456}
        assert result.data.status == {"id": 789}
        assert result.data.folder_id == 456
        assert result.data.owner_id == "user123"
        assert result.data.labels == ["automation", "regression"]
        assert result.data.custom_fields == {"Component": "Test", "Version": "v2.0"}

    def test_validate_test_case_update_input_valid_partial(self):
        """Test valid test case update input with only some fields."""
        from src.mcp_zephyr_scale_cloud.utils.validation import (
            validate_test_case_update_input,
        )

        data = {
            "name": "Updated test case",
            "status": {"id": 789},
        }

        result = validate_test_case_update_input(data)

        assert result.is_valid
        assert result.data.name == "Updated test case"
        assert result.data.status == {"id": 789}
        assert result.data.objective is None
        assert result.data.estimated_time is None

    def test_validate_test_case_update_input_empty(self):
        """Test valid test case update input with empty data (no updates)."""
        from src.mcp_zephyr_scale_cloud.utils.validation import (
            validate_test_case_update_input,
        )

        data = {}

        result = validate_test_case_update_input(data)

        assert result.is_valid
        assert result.data.name is None
        assert result.data.objective is None
        assert result.data.status is None

    def test_validate_test_case_update_input_invalid_name_empty(self):
        """Test invalid test case update input with empty name."""
        from src.mcp_zephyr_scale_cloud.utils.validation import (
            validate_test_case_update_input,
        )

        data = {"name": ""}

        result = validate_test_case_update_input(data)

        assert not result.is_valid
        assert "String should have at least 1 character" in " ".join(result.errors)

    def test_validate_test_case_update_input_invalid_estimated_time(self):
        """Test invalid test case update input with negative estimated time."""
        from src.mcp_zephyr_scale_cloud.utils.validation import (
            validate_test_case_update_input,
        )

        data = {"estimatedTime": -100}

        result = validate_test_case_update_input(data)

        assert not result.is_valid
        assert "greater than or equal to 0" in " ".join(result.errors)

    def test_validate_test_case_update_input_invalid_component_id(self):
        """Test invalid test case update input with invalid component type."""
        from src.mcp_zephyr_scale_cloud.utils.validation import (
            validate_test_case_update_input,
        )

        data = {"component": "not_a_dict"}

        result = validate_test_case_update_input(data)

        assert not result.is_valid
        assert len(result.errors) > 0

    def test_validate_test_case_update_input_invalid_folder_id(self):
        """Test invalid test case update input with invalid folder ID."""
        from src.mcp_zephyr_scale_cloud.utils.validation import (
            validate_test_case_update_input,
        )

        data = {"folderId": 0}  # Should be >= 1

        result = validate_test_case_update_input(data)

        assert not result.is_valid
        assert "greater than or equal to 1" in " ".join(result.errors)

    def test_validate_test_case_update_input_invalid_priority_object(self):
        """Test invalid test case update input with invalid priority type."""
        from src.mcp_zephyr_scale_cloud.utils.validation import (
            validate_test_case_update_input,
        )

        data = {"priority": "not_a_dict"}

        result = validate_test_case_update_input(data)

        assert not result.is_valid
        assert len(result.errors) > 0

    def test_validate_test_case_update_input_invalid_status_object(self):
        """Test invalid test case update input with invalid status type."""
        from src.mcp_zephyr_scale_cloud.utils.validation import (
            validate_test_case_update_input,
        )

        data = {"status": "not_a_dict"}

        result = validate_test_case_update_input(data)

        assert not result.is_valid
        assert len(result.errors) > 0

    def test_validate_test_case_update_input_invalid_type(self):
        """Test invalid test case update input with wrong field types."""
        from src.mcp_zephyr_scale_cloud.utils.validation import (
            validate_test_case_update_input,
        )

        data = {
            "name": 123,  # Should be string
            "estimatedTime": "invalid",  # Should be int
            "labels": "not_a_list",  # Should be list
        }

        result = validate_test_case_update_input(data)

        assert not result.is_valid
        assert len(result.errors) >= 3  # Multiple validation errors

    def test_validate_test_case_update_input_exception_handling(self):
        """Test test case update input validation exception handling."""
        from src.mcp_zephyr_scale_cloud.utils.validation import (
            validate_test_case_update_input,
        )

        # Pass invalid data type to trigger exception
        result = validate_test_case_update_input(None)

        assert not result.is_valid
        assert "Unexpected validation error" in result.errors[0]


class TestCursorPaginationValidation:
    """Test cases for cursor-based pagination validation."""

    def test_validate_cursor_pagination_params_valid(self):
        """Test valid cursor pagination parameters."""
        from src.mcp_zephyr_scale_cloud.utils.validation import (
            validate_cursor_pagination_params,
        )

        # Test with default values
        result = validate_cursor_pagination_params()
        assert result.is_valid
        assert result.data["limit"] == 10
        assert result.data["startAtId"] == 0

        # Test with custom values
        result = validate_cursor_pagination_params(limit=50, start_at_id=100)
        assert result.is_valid
        assert result.data["limit"] == 50
        assert result.data["startAtId"] == 100

        # Test with max values
        result = validate_cursor_pagination_params(limit=1000, start_at_id=999999)
        assert result.is_valid
        assert result.data["limit"] == 1000
        assert result.data["startAtId"] == 999999

    def test_validate_cursor_pagination_params_invalid_limit(self):
        """Test invalid limit values."""
        from src.mcp_zephyr_scale_cloud.utils.validation import (
            validate_cursor_pagination_params,
        )

        # Test limit too low
        result = validate_cursor_pagination_params(limit=0)
        assert not result.is_valid
        assert "limit must be at least 1" in result.errors

        result = validate_cursor_pagination_params(limit=-1)
        assert not result.is_valid
        assert "limit must be at least 1" in result.errors

        # Test limit too high
        result = validate_cursor_pagination_params(limit=1001)
        assert not result.is_valid
        assert "limit cannot exceed 1000" in result.errors

    def test_validate_cursor_pagination_params_invalid_start_at_id(self):
        """Test invalid start_at_id values."""
        from src.mcp_zephyr_scale_cloud.utils.validation import (
            validate_cursor_pagination_params,
        )

        # Test negative start_at_id
        result = validate_cursor_pagination_params(start_at_id=-1)
        assert not result.is_valid
        assert "start_at_id must be non-negative" in result.errors

        result = validate_cursor_pagination_params(start_at_id=-100)
        assert not result.is_valid
        assert "start_at_id must be non-negative" in result.errors

    def test_validate_cursor_pagination_params_multiple_errors(self):
        """Test multiple validation errors at once."""
        from src.mcp_zephyr_scale_cloud.utils.validation import (
            validate_cursor_pagination_params,
        )

        result = validate_cursor_pagination_params(limit=-1, start_at_id=-5)
        assert not result.is_valid
        assert len(result.errors) == 2
        assert "limit must be at least 1" in result.errors
        assert "start_at_id must be non-negative" in result.errors
