"""Tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError

from src.mcp_zephyr_scale_cloud.schemas.base import CreatedResource, PagedResponse
from src.mcp_zephyr_scale_cloud.schemas.common import ProjectLink
from src.mcp_zephyr_scale_cloud.schemas.priority import (
    CreatePriorityRequest,
    Priority,
    PriorityList,
    UpdatePriorityRequest,
)
from src.mcp_zephyr_scale_cloud.schemas.status import (
    CreateStatusRequest,
    Status,
    StatusList,
    StatusType,
    UpdateStatusRequest,
)


class TestPrioritySchemas:
    """Test cases for priority-related schemas."""

    def test_create_priority_request_valid(self):
        """Test creating a valid CreatePriorityRequest."""
        request = CreatePriorityRequest(
            projectKey="TEST",
            name="High Priority",
            description="High priority item",
            color="#FF0000",
        )

        assert request.projectKey == "TEST"
        assert request.name == "High Priority"
        assert request.description == "High priority item"
        assert request.color == "#FF0000"

    def test_create_priority_request_minimal(self):
        """Test creating CreatePriorityRequest with minimal data."""
        request = CreatePriorityRequest(projectKey="TEST", name="Priority")

        assert request.projectKey == "TEST"
        assert request.name == "Priority"
        assert request.description is None
        assert request.color is None

    def test_create_priority_request_invalid_project_key(self):
        """Test CreatePriorityRequest with invalid project key."""
        with pytest.raises(ValidationError, match="String should match pattern"):
            CreatePriorityRequest(
                projectKey="invalid-key", name="Priority"  # Should be uppercase
            )

    def test_create_priority_request_invalid_color(self):
        """Test CreatePriorityRequest with invalid color."""
        with pytest.raises(ValidationError, match="String should match pattern"):
            CreatePriorityRequest(
                projectKey="TEST",
                name="Priority",
                color="invalid-color",  # Should be hex
            )

    def test_create_priority_request_long_name(self):
        """Test CreatePriorityRequest with name too long."""
        with pytest.raises(
            ValidationError, match="String should have at most 255 characters"
        ):
            CreatePriorityRequest(projectKey="TEST", name="x" * 256)  # Too long

    def test_update_priority_request_valid(self):
        """Test creating a valid UpdatePriorityRequest."""
        project = ProjectLink(id=123, self="https://api.example.com/projects/123")
        request = UpdatePriorityRequest(
            id=1,
            project=project,
            name="Updated Priority",
            index=0,
            default=True,
            description="Updated description",
            color="#00FF00",
        )

        assert request.id == 1
        assert request.project.id == 123
        assert request.name == "Updated Priority"
        assert request.index == 0
        assert request.default is True

    def test_priority_schema_valid(self, sample_priority_data):
        """Test creating Priority schema from valid data."""
        priority = Priority(**sample_priority_data)

        assert priority.id == 1
        assert priority.name == "High"
        assert priority.description == "High priority test item"
        assert priority.color == "#FF0000"
        assert priority.project.id == 123

    def test_priority_list_valid(self, sample_priority_list):
        """Test creating PriorityList schema from valid data."""
        priority_list = PriorityList(**sample_priority_list)

        assert len(priority_list.values) == 2
        assert priority_list.total == 2
        assert priority_list.maxResults == 50
        assert priority_list.startAt == 0
        assert priority_list.isLast is True

    def test_model_dump_camelcase(self):
        """Test that model_dump produces camelCase keys."""
        request = CreatePriorityRequest(projectKey="TEST", name="Priority")

        dumped = request.model_dump(exclude_none=True)

        # Should have camelCase key due to alias
        assert "projectKey" in dumped
        assert dumped["projectKey"] == "TEST"
        assert dumped["name"] == "Priority"


class TestBaseSchemas:
    """Test cases for base schemas."""

    def test_created_resource_schema(self, sample_created_resource):
        """Test CreatedResource schema."""
        resource = CreatedResource(**sample_created_resource)

        assert resource.id == 123
        assert resource.key == "CREATED-123"
        assert resource.self == "https://api.example.com/v2/resource/123"

    def test_paged_response_schema(self, sample_priority_list):
        """Test PagedResponse schema with proper aliases."""
        # Test that we can create PagedResponse with camelCase fields
        paged = PagedResponse[Priority](**sample_priority_list)

        assert len(paged.values) == 2
        assert paged.maxResults == 50
        assert paged.startAt == 0
        assert paged.isLast is True


class TestStatusSchemas:
    """Test cases for status-related schemas."""

    def test_create_status_request_valid(self):
        """Test creating a valid CreateStatusRequest."""
        request = CreateStatusRequest(
            project_key="TEST",
            name="In Review",
            type="TEST_EXECUTION",
            description="Test is under review",
            color="#FFA500",
        )

        assert request.project_key == "TEST"
        assert request.name == "In Review"
        assert request.type == StatusType.TEST_EXECUTION
        assert request.description == "Test is under review"
        assert request.color == "#FFA500"

    def test_create_status_request_minimal(self):
        """Test creating CreateStatusRequest with minimal data."""
        request = CreateStatusRequest(
            project_key="TEST", name="Pass", type="TEST_EXECUTION"
        )

        assert request.project_key == "TEST"
        assert request.name == "Pass"
        assert request.type == StatusType.TEST_EXECUTION
        assert request.description is None
        assert request.color is None

    def test_create_status_request_invalid_project_key(self):
        """Test CreateStatusRequest with invalid project key."""
        with pytest.raises(ValidationError, match="String should match pattern"):
            CreateStatusRequest(
                project_key="invalid-key", name="Status", type="TEST_EXECUTION"
            )

    def test_create_status_request_invalid_status_type(self):
        """Test CreateStatusRequest with invalid status type."""
        with pytest.raises(ValidationError, match="Input should be"):
            CreateStatusRequest(project_key="TEST", name="Status", type="INVALID_TYPE")

    def test_create_status_request_invalid_color(self):
        """Test CreateStatusRequest with invalid color."""
        with pytest.raises(ValidationError, match="Color must be in format"):
            CreateStatusRequest(
                project_key="TEST",
                name="Status",
                type="TEST_EXECUTION",
                color="invalid-color",
            )

    def test_create_status_request_long_name(self):
        """Test CreateStatusRequest with too long name."""
        long_name = "x" * 256  # 256 characters, max is 255
        with pytest.raises(ValidationError, match="String should have at most"):
            CreateStatusRequest(
                project_key="TEST", name=long_name, type="TEST_EXECUTION"
            )

    def test_update_status_request_valid(self):
        """Test creating a valid UpdateStatusRequest."""
        request = UpdateStatusRequest(
            project_id=123,
            name="Updated Status",
            index=5,
            default=False,
            archived=False,
            description="Updated description",
            color="#00FF00",
        )

        assert request.project_id == 123
        assert request.name == "Updated Status"
        assert request.index == 5
        assert request.default is False
        assert request.archived is False
        assert request.description == "Updated description"
        assert request.color == "#00FF00"

    def test_status_schema_valid(self, sample_status_data):
        """Test Status schema with valid data."""
        status = Status(**sample_status_data)

        assert status.id == 1
        assert status.name == "In Progress"
        assert status.description == "Test is currently in progress"
        assert status.type == StatusType.TEST_EXECUTION
        assert status.index == 1
        assert status.default is False
        assert status.archived is False
        assert status.color == "#FFA500"
        assert status.project.id == 123
        assert status.self == "https://api.example.com/v2/statuses/1"

    def test_status_list_valid(self, sample_status_list):
        """Test StatusList schema with valid data."""
        status_list = StatusList(**sample_status_list)

        assert len(status_list.values) == 3
        assert status_list.total == 3
        assert status_list.maxResults == 50
        assert status_list.startAt == 0
        assert status_list.isLast is True

        # Test first status
        first_status = status_list.values[0]
        assert first_status.name == "Pass"
        assert first_status.type == StatusType.TEST_EXECUTION
        assert first_status.default is True

    def test_status_type_enum(self):
        """Test StatusType enum values."""
        assert StatusType.TEST_CASE == "TEST_CASE"
        assert StatusType.TEST_PLAN == "TEST_PLAN"
        assert StatusType.TEST_CYCLE == "TEST_CYCLE"
        assert StatusType.TEST_EXECUTION == "TEST_EXECUTION"

        # Test that all enum values are valid
        valid_types = ["TEST_CASE", "TEST_PLAN", "TEST_CYCLE", "TEST_EXECUTION"]
        enum_values = [t.value for t in StatusType]
        assert enum_values == valid_types

    def test_model_dump_camelcase(self):
        """Test that status request models dump to camelCase."""
        request = CreateStatusRequest(
            project_key="TEST",
            name="Status",
            type="TEST_EXECUTION",
            description="Test status",
        )

        dumped = request.model_dump(exclude_none=True, by_alias=True)

        # Should use camelCase aliases for API
        assert "projectKey" in dumped
        assert "project_key" not in dumped
        assert dumped["projectKey"] == "TEST"
        assert dumped["name"] == "Status"
        assert dumped["type"] == "TEST_EXECUTION"
        assert dumped["description"] == "Test status"


class TestCommonSchemas:
    """Test cases for common schemas."""

    def test_project_link_schema(self):
        """Test ProjectLink schema."""
        project = ProjectLink(id=123, self="https://api.example.com/projects/123")

        assert project.id == 123
        assert project.self == "https://api.example.com/projects/123"
