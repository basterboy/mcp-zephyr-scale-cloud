"""Basic integration tests for the MCP server."""

import os

import pytest

from src.mcp_zephyr_scale_cloud.config import ZephyrConfig
from src.mcp_zephyr_scale_cloud.schemas.priority import CreatePriorityRequest
from src.mcp_zephyr_scale_cloud.schemas.status import CreateStatusRequest, StatusType
from src.mcp_zephyr_scale_cloud.server import mcp
from src.mcp_zephyr_scale_cloud.utils.validation import (
    ValidationResult,
    validate_pagination_params,
    validate_project_key,
    validate_status_type,
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
            "get_statuses",
            "get_status",
            "create_status",
            "update_status",
            "get_folders",
            "get_folder",
            "create_folder",
            "get_test_steps",
            "create_test_steps",
            "get_test_script",
            "create_test_script",
            "get_test_case",
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

    def test_status_schema_creation(self):
        """Test creating status request schema."""
        request = CreateStatusRequest(
            project_key="TEST",
            name="In Progress",
            type="TEST_EXECUTION",
            description="Test in progress",
            color="#FFA500",
        )

        assert request.project_key == "TEST"
        assert request.name == "In Progress"
        assert request.type == StatusType.TEST_EXECUTION
        assert request.description == "Test in progress"
        assert request.color == "#FFA500"

    def test_status_schema_validation(self):
        """Test status schema validation."""
        from pydantic import ValidationError

        # Test invalid project key
        with pytest.raises(ValidationError):
            CreateStatusRequest(
                project_key="invalid-key", name="Status", type="TEST_EXECUTION"
            )

        # Test invalid status type
        with pytest.raises(ValidationError):
            CreateStatusRequest(project_key="TEST", name="Status", type="INVALID_TYPE")

    def test_status_type_validation(self):
        """Test status type validation."""
        # Valid cases
        for status_type in ["TEST_CASE", "TEST_PLAN", "TEST_CYCLE", "TEST_EXECUTION"]:
            result = validate_status_type(status_type)
            assert result.is_valid
            assert result.data.value == status_type

        # Invalid cases
        result = validate_status_type("INVALID_TYPE")
        assert not result.is_valid

        result = validate_status_type("")
        assert not result.is_valid

    def test_status_model_dump_camelcase(self):
        """Test that status models use camelCase in output."""
        request = CreateStatusRequest(
            project_key="TEST", name="Status", type="TEST_EXECUTION"
        )

        dumped = request.model_dump(exclude_none=True, by_alias=True)

        # Should have camelCase key due to alias
        assert "projectKey" in dumped
        assert "project_key" not in dumped
        assert dumped["projectKey"] == "TEST"
        assert dumped["name"] == "Status"
        assert dumped["type"] == "TEST_EXECUTION"


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

    def test_folder_schema_creation(self):
        """Test creating folder request schema."""
        from src.mcp_zephyr_scale_cloud.schemas.folder import CreateFolderRequest

        request = CreateFolderRequest(
            project_key="TEST",
            name="Test Folder",
            folder_type="TEST_CASE",
            parent_id=1,
        )

        assert request.project_key == "TEST"
        assert request.name == "Test Folder"
        assert request.folder_type.value == "TEST_CASE"
        assert request.parent_id == 1

    def test_folder_schema_validation(self):
        """Test folder schema validation."""
        from pydantic import ValidationError

        from src.mcp_zephyr_scale_cloud.schemas.folder import CreateFolderRequest

        # Test invalid project key
        with pytest.raises(ValidationError):
            CreateFolderRequest(
                project_key="invalid-key", name="Folder", folder_type="TEST_CASE"
            )

        # Test invalid folder type
        with pytest.raises(ValidationError):
            CreateFolderRequest(
                project_key="TEST", name="Folder", folder_type="INVALID_TYPE"
            )

    def test_folder_type_validation(self):
        """Test folder type validation."""
        from src.mcp_zephyr_scale_cloud.utils.validation import validate_folder_type

        # Valid cases
        for folder_type in ["TEST_CASE", "TEST_PLAN", "TEST_CYCLE"]:
            result = validate_folder_type(folder_type)
            assert result.is_valid
            assert result.data.value == folder_type

        # Invalid cases
        result = validate_folder_type("INVALID_TYPE")
        assert not result.is_valid

        result = validate_folder_type("")
        assert not result.is_valid

    def test_folder_model_dump_camelcase(self):
        """Test that folder models use camelCase in output."""
        from src.mcp_zephyr_scale_cloud.schemas.folder import CreateFolderRequest

        request = CreateFolderRequest(
            project_key="TEST", name="Folder", folder_type="TEST_CASE", parent_id=1
        )

        dumped = request.model_dump(exclude_none=True, by_alias=True)

        # Should have camelCase keys due to aliases
        assert "projectKey" in dumped
        assert "project_key" not in dumped
        assert "folderType" in dumped
        assert "folder_type" not in dumped
        assert "parentId" in dumped
        assert "parent_id" not in dumped
        assert dumped["projectKey"] == "TEST"
        assert dumped["name"] == "Folder"
        assert dumped["folderType"] == "TEST_CASE"
        assert dumped["parentId"] == 1

    def test_test_step_schema_creation(self):
        """Test test step schema creation."""
        from src.mcp_zephyr_scale_cloud.schemas.test_step import (
            TestStep,
            TestStepInline,
            TestStepsList,
            TestStepTestCase,
        )

        # Test inline step
        inline_step = TestStepInline(
            description="Login to application",
            testData="username=admin, password=secret",
            expectedResult="Login successful",
        )
        assert inline_step.description == "Login to application"
        assert inline_step.test_data == "username=admin, password=secret"
        assert inline_step.expected_result == "Login successful"

        # Test step with inline
        step = TestStep(inline=inline_step)
        assert step.inline is not None
        assert step.test_case is None

        # Test case delegation step
        test_case = TestStepTestCase(testCaseKey="PROJ-T123")
        step_with_delegation = TestStep(test_case=test_case)
        assert step_with_delegation.test_case is not None
        assert step_with_delegation.inline is None

        # Test steps list
        steps_list = TestStepsList(
            values=[step, step_with_delegation],
            total=2,
            maxResults=10,
            startAt=0,
            isLast=True,
        )
        assert len(steps_list.values) == 2
        assert steps_list.total == 2

    def test_test_case_key_validation(self):
        """Test test case key validation."""
        from src.mcp_zephyr_scale_cloud.utils.validation import validate_test_case_key

        # Valid cases
        valid_keys = ["PROJ-T123", "ABC-T1", "LONG_PROJECT_NAME-T999"]
        for key in valid_keys:
            result = validate_test_case_key(key)
            assert result.is_valid, f"Key '{key}' should be valid"
            assert result.data == key

        # Invalid cases
        invalid_keys = ["", "PROJ-123", "PROJ-T", "PROJ", "T123", "proj-t123"]
        for key in invalid_keys:
            result = validate_test_case_key(key)
            assert not result.is_valid, f"Key '{key}' should be invalid"

    def test_test_steps_input_creation(self):
        """Test test steps input schema creation and validation."""
        from src.mcp_zephyr_scale_cloud.schemas.test_step import (
            TestStep,
            TestStepInline,
            TestStepsInput,
            TestStepsMode,
        )

        # Create test step
        step = TestStep(
            inline=TestStepInline(
                description="Test login functionality",
                testData="username=admin, password=secret",
                expectedResult="Login successful",
            )
        )

        # Create test steps input
        test_steps_input = TestStepsInput(
            mode=TestStepsMode.APPEND,
            items=[step],
        )

        assert test_steps_input.mode == TestStepsMode.APPEND
        assert len(test_steps_input.items) == 1
        assert test_steps_input.items[0].inline is not None

        # Test model dump with aliases
        dumped = test_steps_input.model_dump(by_alias=True, exclude_none=True)
        assert "mode" in dumped
        assert dumped["mode"] == "APPEND"
        assert "items" in dumped
        assert len(dumped["items"]) == 1

    def test_test_steps_mode_validation(self):
        """Test test steps mode validation."""
        from src.mcp_zephyr_scale_cloud.utils.validation import validate_test_steps_mode

        # Valid modes
        for mode in ["APPEND", "OVERWRITE"]:
            result = validate_test_steps_mode(mode)
            assert result.is_valid, f"Mode '{mode}' should be valid"
            assert result.data == mode

        # Invalid mode
        result = validate_test_steps_mode("INVALID")
        assert not result.is_valid

    def test_test_script_schema_creation(self):
        """Test test script schema creation and validation."""
        from src.mcp_zephyr_scale_cloud.schemas.test_script import (
            TestScript,
            TestScriptInput,
            TestScriptType,
        )

        # Create test script input
        script_input = TestScriptInput(
            type=TestScriptType.PLAIN,
            text="This is a plain text test script for login functionality",
        )

        assert script_input.type == TestScriptType.PLAIN
        assert "login functionality" in script_input.text

        # Create test script
        script = TestScript(
            id=123,
            type=TestScriptType.BDD,
            text=(
                "Given user is on login page\n"
                "When user enters credentials\n"
                "Then user is logged in"
            ),
        )

        assert script.id == 123
        assert script.type == TestScriptType.BDD
        assert "Given user is on login page" in script.text

        # Test empty script (like API response for new test case)
        empty_script = TestScript(
            id=456,
            type=TestScriptType.PLAIN,
            text="",
        )

        assert empty_script.id == 456
        assert empty_script.type == TestScriptType.PLAIN
        assert empty_script.text == ""

        # Test model dump with aliases
        dumped = script_input.model_dump(by_alias=True, exclude_none=True)
        assert "type" in dumped
        assert dumped["type"] == "plain"
        assert "text" in dumped

    def test_test_script_type_validation(self):
        """Test test script type validation."""
        from src.mcp_zephyr_scale_cloud.utils.validation import (
            validate_test_script_type,
        )

        # Valid types
        for script_type in ["plain", "bdd"]:
            result = validate_test_script_type(script_type)
            assert result.is_valid, f"Type '{script_type}' should be valid"
            assert result.data == script_type

        # Invalid type
        result = validate_test_script_type("invalid")
        assert not result.is_valid

    def test_test_script_input_validation(self):
        """Test test script input validation behavior."""
        from src.mcp_zephyr_scale_cloud.utils.validation import (
            validate_test_script_input,
        )

        # Valid script input
        valid_data = {"type": "plain", "text": "Valid script content"}
        result = validate_test_script_input(valid_data)
        assert result.is_valid

        # Empty text should fail for creation
        empty_data = {"type": "plain", "text": ""}
        result = validate_test_script_input(empty_data)
        assert not result.is_valid
        assert "cannot be empty" in result.errors[0]

        # Whitespace-only text should fail for creation
        whitespace_data = {"type": "plain", "text": "   "}
        result = validate_test_script_input(whitespace_data)
        assert not result.is_valid
        assert "cannot be empty" in result.errors[0]

    def test_test_case_schema_creation(self):
        """Test test case schema creation and basic functionality."""
        from src.mcp_zephyr_scale_cloud.schemas.common import ProjectLink
        from src.mcp_zephyr_scale_cloud.schemas.priority import PriorityLink
        from src.mcp_zephyr_scale_cloud.schemas.status import StatusLink
        from src.mcp_zephyr_scale_cloud.schemas.test_case import (
            JiraComponent,
            JiraUserLink,
            TestCase,
        )

        # Test basic test case creation
        test_case = TestCase(
            id=123,
            key="PROJ-T456",
            name="Test login functionality",
            project=ProjectLink(
                id=10001, self="https://api.example.com/projects/10001"
            ),
            priority=PriorityLink(id=2, self="https://api.example.com/priorities/2"),
            status=StatusLink(id=1, self="https://api.example.com/statuses/1"),
            objective="Verify that users can log in successfully",
            precondition="User account exists and is active",
            estimatedTime=300000,  # Use camelCase for API compatibility
            labels=["Regression", "Authentication"],
        )

        assert test_case.id == 123
        assert test_case.key == "PROJ-T456"
        assert test_case.name == "Test login functionality"
        assert test_case.project.id == 10001
        assert test_case.priority.id == 2
        assert test_case.status.id == 1
        assert test_case.objective == "Verify that users can log in successfully"
        assert test_case.estimated_time == 300000
        assert test_case.labels == ["Regression", "Authentication"]

        # Test model dump with aliases
        dumped = test_case.model_dump(by_alias=True, exclude_none=True)
        assert "estimatedTime" in dumped
        assert "estimated_time" not in dumped
        assert dumped["estimatedTime"] == 300000

        # Test JiraComponent
        component = JiraComponent(
            id=10001, self="https://jira.example.com/component/10001"
        )
        assert component.id == 10001

        # Test JiraUserLink
        user = JiraUserLink(accountId="user123")
        assert user.account_id == "user123"

    def test_test_case_with_links_and_custom_fields(self):
        """Test test case with links and custom fields."""
        from src.mcp_zephyr_scale_cloud.schemas.common import ProjectLink
        from src.mcp_zephyr_scale_cloud.schemas.priority import PriorityLink
        from src.mcp_zephyr_scale_cloud.schemas.status import StatusLink
        from src.mcp_zephyr_scale_cloud.schemas.test_case import (
            IssueLink,
            TestCase,
            TestCaseLinkList,
            WebLink,
        )
        from src.mcp_zephyr_scale_cloud.utils.formatting import format_test_case_display

        # Test case with full links and custom fields
        test_case = TestCase(
            id=123,
            key="PROJ-T456",
            name="Test with links",
            project=ProjectLink(
                id=10001, self="https://api.example.com/projects/10001"
            ),
            priority=PriorityLink(id=2, self="https://api.example.com/priorities/2"),
            status=StatusLink(id=1, self="https://api.example.com/statuses/1"),
            customFields={
                "Components": ["PPO initiative"],
                "Version": None,
                "Priority": "High",
                "Tags": ["UI", "Backend"],
            },
            links=TestCaseLinkList(
                self="https://api.example.com/testcases/PROJ-T456/links",
                issues=[
                    IssueLink(
                        id=1001,
                        issueId=2051212,
                        self="https://api.example.com/links/1001",
                        target="https://jira.example.com/issue/2051212",
                        type="COVERAGE",
                    )
                ],
                webLinks=[
                    WebLink(
                        id=2001,
                        self="https://api.example.com/weblinks/2001",
                        description="Related documentation",
                        url="https://docs.example.com/feature",
                        type="RELATED",
                    )
                ],
            ),
        )

        assert test_case.custom_fields is not None
        custom_fields_dict = test_case.custom_fields.model_dump()
        assert "Components" in custom_fields_dict
        assert custom_fields_dict["Components"] == ["PPO initiative"]
        assert custom_fields_dict["Priority"] == "High"

        assert test_case.links is not None
        assert len(test_case.links.issues) == 1
        assert len(test_case.links.web_links) == 1
        assert test_case.links.issues[0].issue_id == 2051212
        assert test_case.links.issues[0].type == "COVERAGE"
        assert test_case.links.web_links[0].url == "https://docs.example.com/feature"

        # Test formatting includes custom fields and links
        formatted = format_test_case_display(test_case)
        assert "Custom Fields:" in formatted
        assert "Components: PPO initiative" in formatted
        assert "Priority: High" in formatted
        assert "Links:" in formatted
        assert "Issues (1):" in formatted
        assert "COVERAGE: Issue 2051212" in formatted
        assert "Web Links (1):" in formatted
        assert "https://docs.example.com/feature" in formatted

    def test_version_schema_creation(self):
        """Test version schema creation and basic functionality."""
        from src.mcp_zephyr_scale_cloud.schemas.version import (
            TestCaseVersionLink,
            TestCaseVersionList,
        )

        # Test TestCaseVersionLink
        version_link = TestCaseVersionLink(
            id=123, self="https://api.example.com/testcases/PROJ-T1/versions/1"
        )
        assert version_link.id == 123
        assert (
            version_link.self == "https://api.example.com/testcases/PROJ-T1/versions/1"
        )

        # Test TestCaseVersionList
        version_list = TestCaseVersionList(
            values=[version_link],
            startAt=0,
            maxResults=10,
            total=1,
            isLast=True,
        )
        assert len(version_list.values) == 1
        assert version_list.values[0].id == 123

    def test_version_number_validation(self):
        """Test version number validation."""
        from src.mcp_zephyr_scale_cloud.utils.validation import validate_version_number

        # Valid version numbers
        result = validate_version_number(1)
        assert result.is_valid
        assert result.data == 1

        result = validate_version_number(100)
        assert result.is_valid
        assert result.data == 100

        # Invalid version numbers
        result = validate_version_number(0)
        assert not result.is_valid
        assert "positive integer" in str(result.errors)

        result = validate_version_number(-1)
        assert not result.is_valid
        assert "positive integer" in str(result.errors)
