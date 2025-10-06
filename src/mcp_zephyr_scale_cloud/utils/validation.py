"""Validation utilities for Zephyr Scale Cloud API data."""

import re
from typing import Any

from pydantic import ValidationError

from ..schemas.folder import CreateFolderRequest, FolderType
from ..schemas.priority import CreatePriorityRequest, UpdatePriorityRequest
from ..schemas.status import CreateStatusRequest, StatusType, UpdateStatusRequest


class ValidationResult:
    """Result of a validation operation."""

    def __init__(
        self, is_valid: bool, errors: list[str] | None = None, data: Any | None = None
    ):
        self.is_valid = is_valid
        self.errors = errors or []
        self.data = data

    def __bool__(self) -> bool:
        return self.is_valid

    @property
    def error_message(self) -> str:
        """Get formatted error message."""
        if not self.errors:
            return ""
        return "\n".join(f"❌ {error}" for error in self.errors)


def validate_project_key(project_key: str) -> ValidationResult:
    """Validate Jira project key format.

    Args:
        project_key: Project key to validate

    Returns:
        ValidationResult with validation status and any errors
    """
    if not project_key:
        return ValidationResult(
            False,
            [
                "No project key provided. Please provide project_key "
                "parameter or set ZEPHYR_SCALE_DEFAULT_PROJECT_KEY env variable"
            ],
        )

    # Jira project keys must be uppercase letters, numbers, and underscores
    # Must start with a letter
    pattern = r"^[A-Z][A-Z0-9_]*$"
    if not re.match(pattern, project_key):
        return ValidationResult(
            False,
            [
                f"Project key '{project_key}' is invalid. Must start with a letter "
                "and contain only uppercase letters, numbers, and underscores."
            ],
        )

    if len(project_key) > 10:  # Jira project key limit
        return ValidationResult(False, ["Project key cannot exceed 10 characters"])

    return ValidationResult(True, data=project_key)


def validate_priority_data(
    data: dict[str, Any], is_update: bool = False
) -> ValidationResult:
    """Validate priority data using Pydantic schemas.

    Args:
        data: Raw data to validate
        is_update: Whether this is for an update operation

    Returns:
        ValidationResult with validation status and parsed data
    """
    try:
        if is_update:
            validated_data = UpdatePriorityRequest(**data)
        else:
            validated_data = CreatePriorityRequest(**data)

        return ValidationResult(True, data=validated_data)

    except ValidationError as e:
        errors = []
        for error in e.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            errors.append(f"Field '{field}': {message}")

        return ValidationResult(False, errors)
    except Exception as e:
        return ValidationResult(False, [f"Validation error: {str(e)}"])


def validate_pagination_params(
    max_results: int | None = None, start_at: int | None = None
) -> ValidationResult:
    """Validate pagination parameters.

    Args:
        max_results: Maximum number of results to return
        start_at: Starting index for pagination

    Returns:
        ValidationResult with validation status
    """
    errors = []

    if max_results is not None:
        if max_results < 1:
            errors.append("max_results must be at least 1")
        elif max_results > 1000:
            errors.append("max_results cannot exceed 1000")

    if start_at is not None:
        if start_at < 0:
            errors.append("start_at must be non-negative")
        elif start_at > 1000000:
            errors.append("start_at cannot exceed 1,000,000")

    if errors:
        return ValidationResult(False, errors)

    return ValidationResult(
        True, data={"maxResults": max_results or 50, "startAt": start_at or 0}
    )


def validate_api_response(
    response_data: dict[str, Any], expected_schema: type
) -> ValidationResult:
    """Validate API response data against a Pydantic schema.

    Args:
        response_data: Raw response data from API
        expected_schema: Pydantic schema class to validate against

    Returns:
        ValidationResult with validation status and parsed data
    """
    try:
        validated_data = expected_schema(**response_data)
        return ValidationResult(True, data=validated_data)

    except ValidationError as e:
        errors = []
        for error in e.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            errors.append(f"API response field '{field}': {message}")

        return ValidationResult(False, errors)
    except Exception as e:
        return ValidationResult(False, [f"Response validation error: {str(e)}"])


def sanitize_input(value: Any) -> Any:
    """Sanitize user input for safe processing.

    Args:
        value: Input value to sanitize

    Returns:
        Sanitized value
    """
    if isinstance(value, str):
        # Strip whitespace and normalize
        sanitized = value.strip()
        # Remove any null bytes
        sanitized = sanitized.replace("\x00", "")
        return sanitized

    return value


def validate_status_data(
    data: dict[str, Any], is_update: bool = False
) -> ValidationResult:
    """Validate status data using appropriate Pydantic schema.

    Args:
        data: Dictionary of status data to validate
        is_update: Whether this is for an update operation

    Returns:
        ValidationResult with validation status and validated data or errors
    """
    try:
        if is_update:
            validated_status = UpdateStatusRequest(**data)
        else:
            validated_status = CreateStatusRequest(**data)

        return ValidationResult(True, data=validated_status)

    except ValidationError as e:
        errors = []
        for error in e.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            errors.append(f"Field '{field}': {message}")

        return ValidationResult(False, errors)

    except Exception as e:
        return ValidationResult(False, [f"Unexpected validation error: {str(e)}"])


def validate_status_type(status_type: str) -> ValidationResult:
    """Validate status type value.

    Args:
        status_type: Status type to validate

    Returns:
        ValidationResult with validation status and any errors
    """
    try:
        validated_type = StatusType(status_type)
        return ValidationResult(True, data=validated_type)
    except ValueError:
        valid_types = [t.value for t in StatusType]
        return ValidationResult(
            False,
            [
                f"Invalid status type '{status_type}'. "
                f"Valid types: {', '.join(valid_types)}"
            ],
        )


def validate_folder_data(data: dict[str, Any]) -> ValidationResult:
    """Validate folder data using CreateFolderRequest Pydantic schema.

    Args:
        data: Dictionary of folder data to validate

    Returns:
        ValidationResult with validation status and validated data or errors
    """
    try:
        validated_folder = CreateFolderRequest(**data)
        return ValidationResult(True, data=validated_folder)

    except ValidationError as e:
        errors = []
        for error in e.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            errors.append(f"Field '{field}': {message}")

        return ValidationResult(False, errors)

    except Exception as e:
        return ValidationResult(False, [f"Unexpected validation error: {str(e)}"])


def validate_folder_type(folder_type: str) -> ValidationResult:
    """Validate folder type value.

    Args:
        folder_type: Folder type to validate

    Returns:
        ValidationResult with validation status and any errors
    """
    try:
        validated_type = FolderType(folder_type)
        return ValidationResult(True, data=validated_type)
    except ValueError:
        valid_types = [t.value for t in FolderType]
        return ValidationResult(
            False,
            [
                f"Invalid folder type '{folder_type}'. "
                f"Valid types: {', '.join(valid_types)}"
            ],
        )


def validate_test_case_key(test_case_key: str) -> "ValidationResult[str]":
    """
    Validate test case key format.

    Args:
        test_case_key: Test case key to validate

    Returns:
        ValidationResult with validated test case key or error messages
    """
    import re

    if not test_case_key:
        return ValidationResult(False, ["Test case key is required"])

    # Pattern from OpenAPI: (.+-T[0-9]+)
    pattern = r"^.+-T[0-9]+$"
    if not re.match(pattern, test_case_key):
        return ValidationResult(
            False,
            [
                f"Invalid test case key format '{test_case_key}'. "
                "Expected format: [PROJECT]-T[NUMBER] (e.g., 'PROJ-T123')"
            ],
        )

    return ValidationResult(True, data=test_case_key)


def validate_test_steps_input(test_steps_input_data: dict) -> "ValidationResult":
    """
    Validate test steps input data.

    Args:
        test_steps_input_data: Dictionary containing test steps input data

    Returns:
        ValidationResult with validated TestStepsInput or error messages
    """
    from ..schemas.test_step import TestStepsInput

    try:
        validated_input = TestStepsInput(**test_steps_input_data)
        return ValidationResult(True, data=validated_input)
    except ValueError as e:
        return ValidationResult(False, [f"Invalid test steps input: {str(e)}"])


def validate_test_steps_mode(mode: str) -> "ValidationResult[str]":
    """
    Validate test steps mode.

    Args:
        mode: Mode string to validate

    Returns:
        ValidationResult with validated mode or error messages
    """
    from ..schemas.test_step import TestStepsMode

    try:
        validated_mode = TestStepsMode(mode)
        return ValidationResult(True, data=validated_mode.value)
    except ValueError:
        valid_modes = [mode.value for mode in TestStepsMode]
        return ValidationResult(
            False,
            [
                f"Invalid test steps mode '{mode}'. "
                f"Valid modes: {', '.join(valid_modes)}"
            ],
        )


def validate_test_script_input(test_script_input_data: dict) -> "ValidationResult":
    """
    Validate test script input data.

    Args:
        test_script_input_data: Dictionary containing test script input data

    Returns:
        ValidationResult with validated TestScriptInput or error messages
    """
    from ..schemas.test_script import TestScriptInput

    try:
        # Validate that text has content when creating (not reading)
        if (
            "text" in test_script_input_data
            and len(test_script_input_data["text"].strip()) == 0
        ):
            return ValidationResult(
                False, ["Test script text cannot be empty when creating a script"]
            )

        validated_input = TestScriptInput(**test_script_input_data)
        return ValidationResult(True, data=validated_input)
    except ValueError as e:
        return ValidationResult(False, [f"Invalid test script input: {str(e)}"])


def validate_test_script_type(script_type: str) -> "ValidationResult[str]":
    """
    Validate test script type.

    Args:
        script_type: Script type string to validate

    Returns:
        ValidationResult with validated type or error messages
    """
    from ..schemas.test_script import TestScriptType

    try:
        validated_type = TestScriptType(script_type)
        return ValidationResult(True, data=validated_type.value)
    except ValueError:
        valid_types = [t.value for t in TestScriptType]
        return ValidationResult(
            False,
            [
                f"Invalid test script type '{script_type}'. "
                f"Valid types: {', '.join(valid_types)}"
            ],
        )


def validate_version_number(version: int) -> "ValidationResult[int]":
    """
    Validate version number.

    Args:
        version: Version number to validate

    Returns:
        ValidationResult with validated version or error messages
    """
    if not isinstance(version, int) or version < 1:
        return ValidationResult(
            False,
            ["Version must be a positive integer (1 or greater)"],
        )
    return ValidationResult(True, data=version)


def validate_issue_link_input(issue_link_data: dict) -> "ValidationResult":
    """
    Validate issue link input data.

    Args:
        issue_link_data: Dictionary containing issue link input data

    Returns:
        ValidationResult with validated IssueLinkInput or error messages
    """
    from ..schemas.test_case import IssueLinkInput

    try:
        validated_input = IssueLinkInput(**issue_link_data)
        return ValidationResult(True, data=validated_input)

    except ValidationError as e:
        errors = []
        for error in e.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            errors.append(f"Field '{field}': {message}")

        return ValidationResult(False, errors)

    except Exception as e:
        return ValidationResult(False, [f"Unexpected validation error: {str(e)}"])


def validate_web_link_input(web_link_data: dict) -> "ValidationResult":
    """
    Validate web link input data.

    Args:
        web_link_data: Dictionary containing web link input data

    Returns:
        ValidationResult with validated WebLinkInput or error messages
    """
    from ..schemas.test_case import WebLinkInput

    try:
        validated_input = WebLinkInput(**web_link_data)
        return ValidationResult(True, data=validated_input)

    except ValidationError as e:
        errors = []
        for error in e.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            errors.append(f"Field '{field}': {message}")

        return ValidationResult(False, errors)

    except Exception as e:
        return ValidationResult(False, [f"Unexpected validation error: {str(e)}"])


def validate_issue_id(issue_id: int) -> "ValidationResult[int]":
    """
    Validate Jira issue ID.

    Args:
        issue_id: Issue ID to validate

    Returns:
        ValidationResult with validated issue ID or error messages
    """
    if not isinstance(issue_id, int) or issue_id < 1:
        errors = ["Issue ID must be a positive integer (1 or greater)"]

        # Check if user might have provided an issue key instead of ID
        if isinstance(issue_id, str) and "-" in str(issue_id):
            errors.append(
                f"It looks like you provided an issue key ('{issue_id}') "
                "instead of an issue ID"
            )
            errors.append("Please provide the numeric Jira issue ID, not the issue key")
            errors.append(
                "Tip: Use the Atlassian/Jira MCP tool to look up the issue ID "
                "from the key"
            )
        elif not isinstance(issue_id, int):
            errors.append(f"Received {type(issue_id).__name__}: {issue_id}")
            errors.append(
                "If you have an issue key (e.g., 'PROJ-1234'), use the "
                "Atlassian/Jira MCP tool to get the issue ID"
            )

        return ValidationResult(False, errors)

    return ValidationResult(True, data=issue_id)


def validate_test_case_input(test_case_data: dict) -> "ValidationResult":
    """
    Validate test case input data.

    Args:
        test_case_data: Dictionary containing test case input data

    Returns:
        ValidationResult with validated TestCaseInput or error messages
    """
    from ..schemas.test_case import TestCaseInput

    try:
        validated_input = TestCaseInput(**test_case_data)
        return ValidationResult(True, data=validated_input)

    except ValidationError as e:
        errors = []
        for error in e.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            errors.append(f"Field '{field}': {message}")

        return ValidationResult(False, errors)

    except Exception as e:
        return ValidationResult(False, [f"Unexpected validation error: {str(e)}"])


def validate_test_case_update_input(test_case_data: dict) -> "ValidationResult":
    """
    Validate test case update input data.

    Args:
        test_case_data: Dictionary containing test case update data

    Returns:
        ValidationResult with validated TestCaseUpdateInput or error messages
    """
    from ..schemas.test_case import TestCaseUpdateInput

    try:
        validated_input = TestCaseUpdateInput(**test_case_data)
        return ValidationResult(True, data=validated_input)

    except ValidationError as e:
        errors = []
        for error in e.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            errors.append(f"Field '{field}': {message}")

        return ValidationResult(False, errors)

    except Exception as e:
        return ValidationResult(False, [f"Unexpected validation error: {str(e)}"])


def validate_test_case_name(name: str) -> "ValidationResult[str]":
    """
    Validate test case name.

    Args:
        name: Test case name to validate

    Returns:
        ValidationResult with validated name or error messages
    """
    if not isinstance(name, str):
        return ValidationResult(
            False,
            [f"Name must be a string, got {type(name).__name__}"],
        )

    # Remove leading/trailing whitespace
    name = name.strip()

    if not name:
        return ValidationResult(
            False,
            ["Test case name cannot be empty or only whitespace"],
        )

    if len(name) > 255:
        return ValidationResult(
            False,
            [f"Test case name too long: {len(name)} characters (max 255)"],
        )

    return ValidationResult(True, data=name)


def validate_estimated_time(estimated_time: int) -> "ValidationResult[int]":
    """
    Validate estimated time in milliseconds.

    Args:
        estimated_time: Estimated time to validate

    Returns:
        ValidationResult with validated time or error messages
    """
    if not isinstance(estimated_time, int) or estimated_time < 0:
        return ValidationResult(
            False,
            ["Estimated time must be a non-negative integer (milliseconds)"],
        )
    return ValidationResult(True, data=estimated_time)


def validate_folder_id(folder_id: int) -> "ValidationResult[int]":
    """
    Validate folder ID.

    Args:
        folder_id: Folder ID to validate

    Returns:
        ValidationResult with validated folder ID or error messages
    """
    if not isinstance(folder_id, int) or folder_id < 1:
        return ValidationResult(
            False,
            ["Folder ID must be a positive integer (1 or greater)"],
        )
    return ValidationResult(True, data=folder_id)


def validate_component_id(component_id: int) -> "ValidationResult[int]":
    """
    Validate Jira component ID.

    Args:
        component_id: Component ID to validate

    Returns:
        ValidationResult with validated component ID or error messages
    """
    if not isinstance(component_id, int) or component_id < 0:
        return ValidationResult(
            False,
            ["Component ID must be a non-negative integer"],
        )
    return ValidationResult(True, data=component_id)


def validate_test_cycle_key(test_cycle_key: str) -> ValidationResult:
    """Validate test cycle key format.

    Test cycle keys follow the pattern: [PROJECT_KEY]-R[NUMBER]
    Examples: PROJ-R1, TEST-R123

    Args:
        test_cycle_key: Test cycle key to validate

    Returns:
        ValidationResult with validation status and any errors
    """
    if not test_cycle_key:
        return ValidationResult(False, ["Test cycle key is required"])

    # Test cycle keys follow pattern: [A-Z]+-R[0-9]+
    pattern = r"^[A-Z][A-Z0-9_]+-R[0-9]+$"
    if not re.match(pattern, test_cycle_key):
        return ValidationResult(
            False,
            [
                f"Test cycle key '{test_cycle_key}' is invalid. "
                "Must follow format: [PROJECT]-R[NUMBER] (e.g., PROJ-R123)"
            ],
        )

    return ValidationResult(True, data=test_cycle_key)


def validate_test_cycle_input(test_cycle_data: dict) -> ValidationResult:
    """Validate test cycle input data using Pydantic schema.

    Args:
        test_cycle_data: Raw test cycle data to validate

    Returns:
        ValidationResult with validation status and parsed TestCycleInput
    """
    try:
        from ..schemas.test_cycle import TestCycleInput

        validated_data = TestCycleInput(**test_cycle_data)
        return ValidationResult(True, data=validated_data)

    except ValidationError as e:
        errors = []
        for error in e.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            errors.append(f"Field '{field}': {message}")
        return ValidationResult(False, errors)
    except Exception as e:
        return ValidationResult(False, [f"Unexpected validation error: {str(e)}"])


def validate_test_cycle_update_input(test_cycle_data: dict) -> ValidationResult:
    """Validate test cycle update data using Pydantic schema.

    Args:
        test_cycle_data: Raw test cycle data to validate for update

    Returns:
        ValidationResult with validation status and parsed TestCycle
    """
    try:
        from ..schemas.test_cycle import TestCycle

        validated_data = TestCycle(**test_cycle_data)
        return ValidationResult(True, data=validated_data)

    except ValidationError as e:
        errors = []
        for error in e.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            errors.append(f"Field '{field}': {message}")
        return ValidationResult(False, errors)
    except Exception as e:
        return ValidationResult(False, [f"Unexpected validation error: {str(e)}"])


def validate_jira_version_id(version_id: str | int) -> ValidationResult:
    """Validate Jira project version ID.

    Args:
        version_id: Jira version ID to validate (can be string or int)

    Returns:
        ValidationResult with validated integer version ID or error messages
    """
    try:
        parsed_id = int(version_id)
        if parsed_id < 1:
            return ValidationResult(
                False,
                ["Jira version ID must be a positive integer"],
            )
        return ValidationResult(True, data=parsed_id)
    except (ValueError, TypeError):
        return ValidationResult(
            False,
            [f"Invalid Jira version ID: '{version_id}'. Must be a positive integer"],
        )
