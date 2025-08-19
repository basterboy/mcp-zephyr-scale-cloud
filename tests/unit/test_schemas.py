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


class TestCommonSchemas:
    """Test cases for common schemas."""

    def test_project_link_schema(self):
        """Test ProjectLink schema."""
        project = ProjectLink(id=123, self="https://api.example.com/projects/123")

        assert project.id == 123
        assert project.self == "https://api.example.com/projects/123"
