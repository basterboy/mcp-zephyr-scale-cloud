"""Tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError

from src.mcp_zephyr_scale_cloud.schemas.base import CreatedResource, PagedResponse
from src.mcp_zephyr_scale_cloud.schemas.common import ProjectLink
from src.mcp_zephyr_scale_cloud.schemas.folder import (
    CreateFolderRequest,
    Folder,
    FolderList,
    FolderType,
)
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
            id=123,
            project={"id": 456},
            name="Updated Status",
            index=5,
            default=False,
            archived=False,
            description="Updated description",
            color="#00FF00",
        )

        assert request.id == 123
        assert request.project.id == 456
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
        assert status.index == 1
        assert status.default is False
        assert status.archived is False
        assert status.color == "#FFA500"
        assert status.project.id == 123

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


class TestFolderSchemas:
    """Test cases for folder-related schemas."""

    def test_create_folder_request_valid(self):
        """Test creating a valid CreateFolderRequest."""
        request = CreateFolderRequest(
            projectKey="TEST",
            name="Test Folder",
            folderType="TEST_CASE",
            parentId=1,
        )

        assert request.project_key == "TEST"
        assert request.name == "Test Folder"
        assert request.folder_type == FolderType.TEST_CASE
        assert request.parent_id == 1

    def test_create_folder_request_minimal(self):
        """Test creating CreateFolderRequest with minimal data (root folder)."""
        request = CreateFolderRequest(
            projectKey="TEST", name="Root Folder", folderType="TEST_PLAN"
        )

        assert request.project_key == "TEST"
        assert request.name == "Root Folder"
        assert request.folder_type == FolderType.TEST_PLAN
        assert request.parent_id is None

    def test_create_folder_request_invalid_project_key(self):
        """Test CreateFolderRequest with invalid project key."""
        with pytest.raises(ValidationError) as exc_info:
            CreateFolderRequest(
                projectKey="invalid", name="Folder", folderType="TEST_CASE"
            )

        errors = exc_info.value.errors()
        assert any("String should match pattern" in str(error) for error in errors)

    def test_create_folder_request_invalid_folder_type(self):
        """Test CreateFolderRequest with invalid folder type."""
        with pytest.raises(ValidationError) as exc_info:
            CreateFolderRequest(
                projectKey="TEST", name="Folder", folderType="INVALID_TYPE"
            )

        errors = exc_info.value.errors()
        assert any("Input should be" in str(error) for error in errors)

    def test_create_folder_request_long_name(self):
        """Test CreateFolderRequest with name too long."""
        long_name = "x" * 256  # Max is 255
        with pytest.raises(ValidationError) as exc_info:
            CreateFolderRequest(
                projectKey="TEST", name=long_name, folderType="TEST_CASE"
            )

        errors = exc_info.value.errors()
        assert any(
            "String should have at most 255 characters" in str(error)
            for error in errors
        )

    def test_create_folder_request_empty_name(self):
        """Test CreateFolderRequest with empty name."""
        with pytest.raises(ValidationError) as exc_info:
            CreateFolderRequest(projectKey="TEST", name="", folderType="TEST_CASE")

        errors = exc_info.value.errors()
        assert any(
            "String should have at least 1 character" in str(error) for error in errors
        )

    def test_folder_schema_valid(self, sample_folder_data):
        """Test creating a valid Folder from API response."""
        folder = Folder(**sample_folder_data)

        assert folder.id == 1
        assert folder.parent_id is None
        assert folder.name == "Test Cases"
        assert folder.index == 0
        assert folder.folder_type == FolderType.TEST_CASE
        assert folder.project.id == 123

    def test_folder_list_valid(self, sample_folder_list):
        """Test creating a valid FolderList from API response."""
        folder_list = FolderList(**sample_folder_list)

        assert len(folder_list.values) == 3
        assert folder_list.total == 3
        assert folder_list.maxResults == 50
        assert folder_list.startAt == 0
        assert folder_list.isLast is True

        # Test first folder
        first_folder = folder_list.values[0]
        assert first_folder.name == "Test Cases"
        assert first_folder.folder_type == FolderType.TEST_CASE
        assert first_folder.parent_id is None

        # Test second folder (child)
        second_folder = folder_list.values[1]
        assert second_folder.name == "Smoke Tests"
        assert second_folder.parent_id == 1

    def test_folder_type_enum(self):
        """Test FolderType enum values."""
        assert FolderType.TEST_CASE == "TEST_CASE"
        assert FolderType.TEST_PLAN == "TEST_PLAN"
        assert FolderType.TEST_CYCLE == "TEST_CYCLE"

        # Test that all enum values are valid
        valid_types = ["TEST_CASE", "TEST_PLAN", "TEST_CYCLE"]
        enum_values = [t.value for t in FolderType]
        assert enum_values == valid_types

    def test_model_dump_camelcase(self):
        """Test that folder request models dump to camelCase."""
        request = CreateFolderRequest(
            project_key="TEST",
            name="Test Folder",
            folder_type="TEST_CASE",
            parent_id=1,
        )

        dumped = request.model_dump(exclude_none=True, by_alias=True)

        # Should use camelCase aliases for API
        assert "projectKey" in dumped
        assert "project_key" not in dumped
        assert "folderType" in dumped
        assert "folder_type" not in dumped
        assert "parentId" in dumped
        assert "parent_id" not in dumped
        assert dumped["projectKey"] == "TEST"
        assert dumped["name"] == "Test Folder"
        assert dumped["folderType"] == "TEST_CASE"
        assert dumped["parentId"] == 1


class TestTestCycleSchemas:
    """Test test cycle Pydantic schemas."""

    def test_jira_project_version_valid(self):
        """Test creating valid JiraProjectVersion."""
        from mcp_zephyr_scale_cloud.schemas.test_cycle import JiraProjectVersion

        version = JiraProjectVersion(id=123)
        assert version.id == 123

    def test_test_cycle_input_minimal(self):
        """Test creating TestCycleInput with minimal required fields."""
        from mcp_zephyr_scale_cloud.schemas.test_cycle import TestCycleInput

        test_cycle_input = TestCycleInput(project_key="PROJ", name="Sprint 1 Testing")
        assert test_cycle_input.project_key == "PROJ"
        assert test_cycle_input.name == "Sprint 1 Testing"
        assert test_cycle_input.description is None

    def test_test_cycle_input_full(self):
        """Test creating TestCycleInput with all fields."""
        from mcp_zephyr_scale_cloud.schemas.test_cycle import TestCycleInput

        test_cycle_input = TestCycleInput(
            project_key="PROJ",
            name="Sprint 1 Testing",
            description="Testing cycle for sprint 1",
            planned_start_date="2025-01-15T09:00:00Z",
            planned_end_date="2025-01-22T17:00:00Z",
            jira_project_version="10000",
            status_name="In Progress",
            folder_id="123",
            owner_id="account123",
            custom_fields={"Environment": "Production"},
        )
        assert test_cycle_input.project_key == "PROJ"
        assert test_cycle_input.custom_fields == {"Environment": "Production"}

    def test_test_cycle_input_missing_name(self):
        """Test TestCycleInput validation fails without required name."""
        from mcp_zephyr_scale_cloud.schemas.test_cycle import TestCycleInput

        with pytest.raises(ValidationError) as exc_info:
            TestCycleInput(project_key="PROJ")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("name",)

    def test_test_cycle_input_empty_name(self):
        """Test TestCycleInput validation fails with empty name."""
        from mcp_zephyr_scale_cloud.schemas.test_cycle import TestCycleInput

        with pytest.raises(ValidationError):
            TestCycleInput(project_key="PROJ", name="")

    def test_test_cycle_valid_minimal(self):
        """Test creating TestCycle with minimal fields."""
        from mcp_zephyr_scale_cloud.schemas.test_cycle import TestCycle

        test_cycle = TestCycle(
            id=1,
            key="PROJ-R1",
            name="Sprint 1 Testing",
            project={"id": 10000, "key": "PROJ"},
            status={"id": 1, "name": "In Progress"},
        )
        assert test_cycle.id == 1
        assert test_cycle.key == "PROJ-R1"
        assert test_cycle.name == "Sprint 1 Testing"

    def test_test_cycle_key_validation_valid(self):
        """Test TestCycle key validation with valid patterns."""
        from mcp_zephyr_scale_cloud.schemas.test_cycle import TestCycle

        valid_keys = ["PROJ-R1", "ABC-R123", "TEST-R999"]
        for key in valid_keys:
            test_cycle = TestCycle(
                id=1,
                key=key,
                name="Test",
                project={"id": 10000, "key": "PROJ"},
                status={"id": 1, "name": "In Progress"},
            )
            assert test_cycle.key == key

    def test_test_cycle_key_validation_invalid(self):
        """Test TestCycle key validation with invalid patterns."""
        from mcp_zephyr_scale_cloud.schemas.test_cycle import TestCycle

        invalid_keys = ["PROJ-T1", "PROJ-1", "R123"]
        for key in invalid_keys:
            with pytest.raises(ValidationError):
                TestCycle(
                    id=1, key=key, name="Test", project={"id": 10000, "key": "PROJ"}
                )

    def test_test_cycle_list_empty(self):
        """Test creating empty TestCycleList."""
        from mcp_zephyr_scale_cloud.schemas.test_cycle import TestCycleList

        test_cycle_list = TestCycleList(
            maxResults=10, startAt=0, total=0, isLast=True, values=[]
        )
        assert test_cycle_list.total == 0
        assert test_cycle_list.isLast is True

    def test_test_cycle_link_list(self):
        """Test creating TestCycleLinkList."""
        from mcp_zephyr_scale_cloud.schemas.test_cycle import TestCycleLinkList

        link_list = TestCycleLinkList(
            issues=[{"id": 1, "issue_id": 10001}],
            webLinks=[{"id": 2, "url": "https://example.com"}],
        )
        assert len(link_list.issues) == 1
        assert len(link_list.web_links) == 1


class TestTestPlanSchemas:
    """Test cases for test plan-related schemas."""

    def test_test_plan_input_valid(self):
        """Test creating a valid TestPlanInput."""
        from src.mcp_zephyr_scale_cloud.schemas.test_plan import TestPlanInput

        test_plan_input = TestPlanInput(
            projectKey="TEST",
            name="Integration Test Plan",
            objective="Test all integration points",
            folderId=123,
            statusName="Draft",
            ownerId="user123",
            labels=["integration", "smoke"],
            customFields={"Environment": "Staging"},
        )

        assert test_plan_input.project_key == "TEST"
        assert test_plan_input.name == "Integration Test Plan"
        assert test_plan_input.objective == "Test all integration points"
        assert test_plan_input.folder_id == 123
        assert test_plan_input.status_name == "Draft"
        assert test_plan_input.owner_id == "user123"
        assert test_plan_input.labels == ["integration", "smoke"]
        assert test_plan_input.custom_fields.Environment == "Staging"

    def test_test_plan_input_minimal(self):
        """Test creating TestPlanInput with minimal required fields."""
        from src.mcp_zephyr_scale_cloud.schemas.test_plan import TestPlanInput

        test_plan_input = TestPlanInput(
            projectKey="PROJ",
            name="Minimal Plan",
        )

        assert test_plan_input.project_key == "PROJ"
        assert test_plan_input.name == "Minimal Plan"
        assert test_plan_input.objective is None
        assert test_plan_input.folder_id is None

    def test_test_plan_input_missing_required_fields(self):
        """Test that TestPlanInput requires name and projectKey."""
        from src.mcp_zephyr_scale_cloud.schemas.test_plan import TestPlanInput

        with pytest.raises(ValidationError) as exc_info:
            TestPlanInput(projectKey="TEST")

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_test_plan_valid(self):
        """Test creating a valid TestPlan."""
        from src.mcp_zephyr_scale_cloud.schemas.test_plan import TestPlan

        test_plan = TestPlan(
            id=123,
            key="TEST-P10",
            name="Integration Test Plan",
            project={"id": 1000, "key": "TEST"},
            status={"id": 1, "name": "In Progress"},
            objective="Test all features",
            folder={"id": 5, "name": "Test Plans"},
            owner={"accountId": "user123"},
            labels=["integration"],
            customFields={"Release": "v1.0"},
        )

        assert test_plan.id == 123
        assert test_plan.key == "TEST-P10"
        assert test_plan.name == "Integration Test Plan"
        assert test_plan.project.id == 1000
        assert test_plan.status.id == 1
        assert test_plan.objective == "Test all features"

    def test_test_plan_key_validation(self):
        """Test test plan key format validation."""
        from src.mcp_zephyr_scale_cloud.schemas.test_plan import TestPlan

        # Valid key
        test_plan = TestPlan(
            id=1,
            key="PROJ-P123",
            name="Test",
            project={"id": 100, "key": "PROJ"},
            status={"id": 1, "name": "Draft"},
        )
        assert test_plan.key == "PROJ-P123"

        # Invalid key format should raise error
        with pytest.raises(ValidationError) as exc_info:
            TestPlan(
                id=1,
                key="INVALID",
                name="Test",
                project={"id": 100, "key": "PROJ"},
                status={"id": 1, "name": "Draft"},
            )
        errors = exc_info.value.errors()
        assert any("key" in str(error) for error in errors)

    def test_test_plan_list(self):
        """Test creating TestPlanList."""
        from src.mcp_zephyr_scale_cloud.schemas.test_plan import (
            TestPlan,
            TestPlanList,
        )

        test_plan = TestPlan(
            id=1,
            key="TEST-P1",
            name="Plan 1",
            project={"id": 100, "key": "TEST"},
            status={"id": 1, "name": "Draft"},
        )

        test_plan_list = TestPlanList(
            maxResults=10,
            startAt=0,
            total=1,
            isLast=True,
            values=[test_plan],
        )

        assert test_plan_list.maxResults == 10
        assert test_plan_list.startAt == 0
        assert test_plan_list.total == 1
        assert test_plan_list.isLast is True
        assert len(test_plan_list.values) == 1
        assert test_plan_list.values[0].key == "TEST-P1"

    def test_test_plan_test_cycle_link_input(self):
        """Test creating TestPlanTestCycleLinkInput."""
        from src.mcp_zephyr_scale_cloud.schemas.test_plan import (
            TestPlanTestCycleLinkInput,
        )

        # Test with numeric ID as string
        link_input = TestPlanTestCycleLinkInput(testCycleIdOrKey="456")
        assert link_input.test_cycle_id_or_key == "456"

        # Test with test cycle key
        link_input2 = TestPlanTestCycleLinkInput(testCycleIdOrKey="PROJ-R123")
        assert link_input2.test_cycle_id_or_key == "PROJ-R123"

    def test_test_plan_test_cycle_link_input_invalid(self):
        """Test TestPlanTestCycleLinkInput validation."""
        from src.mcp_zephyr_scale_cloud.schemas.test_plan import (
            TestPlanTestCycleLinkInput,
        )

        # Invalid format should fail
        with pytest.raises(ValidationError):
            TestPlanTestCycleLinkInput(testCycleIdOrKey="INVALID")

        with pytest.raises(ValidationError):
            TestPlanTestCycleLinkInput(testCycleIdOrKey="PROJ-T123")  # Wrong type

    def test_web_link_input_with_mandatory_description(self):
        """Test WebLinkInputWithMandatoryDescription."""
        from src.mcp_zephyr_scale_cloud.schemas.test_plan import (
            WebLinkInputWithMandatoryDescription,
        )

        link_input = WebLinkInputWithMandatoryDescription(
            url="https://example.com",
            description="Example link",
        )

        assert link_input.url == "https://example.com"
        assert link_input.description == "Example link"

    def test_web_link_input_missing_description(self):
        """Test that WebLinkInputWithMandatoryDescription requires description."""
        from src.mcp_zephyr_scale_cloud.schemas.test_plan import (
            WebLinkInputWithMandatoryDescription,
        )

        # Missing description
        with pytest.raises(ValidationError) as exc_info:
            WebLinkInputWithMandatoryDescription(url="https://example.com")

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("description",) for error in errors)

        # Empty description
        with pytest.raises(ValidationError):
            WebLinkInputWithMandatoryDescription(
                url="https://example.com", description=""
            )

    def test_test_plan_links(self):
        """Test TestPlanLinks with all link types."""
        from src.mcp_zephyr_scale_cloud.schemas.test_plan import TestPlanLinks

        links = TestPlanLinks(
            webLinks=[{"id": 1, "url": "https://example.com", "type": "RELATED"}],
            issues=[
                {
                    "id": 2,
                    "issueId": 12345,
                    "target": "https://jira.com/issue/12345",
                    "type": "COVERAGE",
                }
            ],
            testCycles=[{"id": 3, "testCycleId": 789, "self": "http://link"}],
        )

        assert len(links.web_links) == 1
        assert len(links.issues) == 1
        assert len(links.test_cycles) == 1
        assert links.test_cycles[0].test_cycle_id == 789
