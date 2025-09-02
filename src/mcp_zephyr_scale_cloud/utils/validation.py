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
        return ValidationResult(False, ["Project key is required"])

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
