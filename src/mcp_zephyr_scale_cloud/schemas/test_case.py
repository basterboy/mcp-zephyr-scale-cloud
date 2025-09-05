"""Pydantic models for Zephyr Scale test case entities."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .base import Link
from .common import CustomFields, ProjectLink
from .folder import FolderLink
from .priority import PriorityLink
from .status import StatusLink

# Type aliases for simple types
EntityId = int
Labels = list[str]


class IssueLinkInput(BaseModel):
    """Input schema for creating issue links."""

    issue_id: int = Field(..., alias="issueId", description="The Jira issue ID", ge=1)


class WebLinkInput(BaseModel):
    """Input schema for creating web links."""

    url: str = Field(
        ...,
        description="The web link URL",
        example="https://atlassian.com",
    )
    description: str | None = Field(
        None, description="The link description", example="A link to atlassian.com"
    )


class TestCaseInput(BaseModel):
    """Input schema for creating test cases."""

    model_config = {"populate_by_name": True}

    project_key: str = Field(
        ...,
        alias="projectKey",
        description="Jira project key",
        pattern=r"([A-Z][A-Z_0-9]+)",
        example="PROJ",
    )
    name: str = Field(
        ...,
        description="The test case name",
        min_length=1,
        example="Test user login functionality",
    )
    objective: str | None = Field(
        None,
        description="The test case objective",
        example="Verify that users can successfully log in with valid credentials",
    )
    precondition: str | None = Field(
        None,
        description="Test case preconditions",
        example="User account exists and is active",
    )
    estimated_time: int | None = Field(
        None,
        alias="estimatedTime",
        description="Estimated duration in milliseconds",
        ge=0,
        example=138000,
    )
    component_id: int | None = Field(
        None,
        alias="componentId",
        description="ID of a component from Jira",
        ge=0,
        example=10001,
    )
    priority_name: str | None = Field(
        None,
        alias="priorityName",
        description="The priority name (defaults to 'Normal' if not specified)",
        max_length=255,
        min_length=1,
        example="High",
    )
    status_name: str | None = Field(
        None,
        alias="statusName",
        description="The status name (defaults to 'Draft' if not specified)",
        max_length=255,
        min_length=1,
        example="Draft",
    )
    folder_id: int | None = Field(
        None,
        alias="folderId",
        description="ID of a folder to place the test case within",
        ge=1,
        example=12345,
    )
    owner_id: str | None = Field(
        None,
        alias="ownerId",
        description="Jira user account ID for the test case owner",
        example="712020:b231ae42-7619-42b4-9cd8-a83e0cdc00ad",
    )
    labels: list[str] | None = Field(
        None,
        description="List of labels for the test case",
        example=["automation", "smoke", "login"],
    )
    custom_fields: dict[str, Any] | None = Field(
        None,
        alias="customFields",
        description="Custom fields for the test case",
        example={"Priority": "High", "Component": "Authentication"},
    )


class TestCaseUpdateInput(BaseModel):
    """Input schema for updating test cases."""

    model_config = {"populate_by_name": True}

    name: str | None = Field(
        None,
        description="The test case name",
        min_length=1,
        example="Updated test user login functionality",
    )
    objective: str | None = Field(
        None,
        description="The test case objective",
        example="Verify that users can successfully log in with valid credentials",
    )
    precondition: str | None = Field(
        None,
        description="Test case preconditions",
        example="User account exists and is active",
    )
    estimated_time: int | None = Field(
        None,
        alias="estimatedTime",
        description="Estimated duration in milliseconds",
        ge=0,
        example=138000,
    )
    component: dict[str, Any] | None = Field(
        None,
        description="ID of the component from Jira to update the test case to",
        example={"id": 10001},
    )
    priority: dict[str, Any] | None = Field(
        None,
        description="ID of the priority to update the test case to",
        example={"id": 123},
    )
    status: dict[str, Any] | None = Field(
        None,
        description="ID of the status to update the test case to",
        example={"id": 456},
    )
    folder_id: int | None = Field(
        None,
        alias="folderId",
        description="ID of a folder to place the test case within",
        ge=1,
        example=12345,
    )
    owner_id: str | None = Field(
        None,
        alias="ownerId",
        description="Jira user account ID for the test case owner",
        example="712020:b231ae42-7619-42b4-9cd8-a83e0cdc00ad",
    )
    labels: list[str] | None = Field(
        None,
        description="List of labels for the test case",
        example=["automation", "smoke", "login"],
    )
    custom_fields: dict[str, Any] | None = Field(
        None,
        alias="customFields",
        description="Custom fields for the test case",
        example={"Priority": "High", "Component": "Authentication"},
    )


class IssueLink(Link):
    """Issue link for test case."""

    id: int = Field(..., description="Link ID", ge=1)
    issue_id: int = Field(..., alias="issueId", description="The Jira issue ID", ge=1)
    target: str = Field(
        ...,
        description="Jira Cloud REST API endpoint for the issue",
        example="https://jira.atlassian.net/rest/api/2/issue/10000",
    )
    type: str = Field(
        ...,
        description="The link type",
        pattern="^(COVERAGE|BLOCKS|RELATED)$",
        example="COVERAGE",
    )


class WebLink(Link):
    """Web link for test case."""

    id: int = Field(..., description="Link ID", ge=1)
    description: str | None = Field(
        None, description="The link description", example="A link to atlassian.com"
    )
    url: str = Field(
        ...,
        description="The web link URL",
        example="https://atlassian.com",
    )
    type: str = Field(
        ...,
        description="The link type",
        pattern="^(COVERAGE|BLOCKS|RELATED)$",
        example="COVERAGE",
    )


class TestCaseLinkList(Link):
    """Test case links container."""

    issues: list[IssueLink] = Field(
        default_factory=list, description="Jira issues linked to this test case"
    )
    web_links: list[WebLink] = Field(
        default_factory=list,
        alias="webLinks",
        description="Web links for this test case",
    )


class JiraComponent(BaseModel):
    """Jira component information."""

    id: int = Field(..., description="Component ID")
    self: str = Field(..., description="Component self URL")


class JiraUserLink(BaseModel):
    """Jira user reference."""

    account_id: str = Field(..., alias="accountId", description="Jira user account ID")


class TestCaseTestScriptLink(Link):
    """Test script link for test case."""

    pass  # Inherits from Link (self field)


class TestCase(BaseModel):
    """Test case entity from Zephyr Scale."""

    # Required fields
    id: EntityId = Field(..., description="Test case ID", ge=1)
    key: str = Field(
        ...,
        description="Test case key",
        pattern=r".+-T[0-9]+",
        example="SA-T10",
    )
    name: str = Field(
        ...,
        description="Test case name",
        min_length=1,
        example="Check axial pump",
    )
    project: ProjectLink = Field(..., description="Project information")
    priority: PriorityLink = Field(..., description="Priority information")
    status: StatusLink = Field(..., description="Status information")

    # Optional fields
    created_on: datetime | None = Field(
        None,
        alias="createdOn",
        description="Creation timestamp",
    )
    objective: str | None = Field(
        None,
        description="Test case objective",
        example="To ensure the axial pump can be enabled",
    )
    precondition: str | None = Field(
        None,
        description="Preconditions for the test",
        example="Latest version of the axial pump available",
    )
    estimated_time: int | None = Field(
        None,
        alias="estimatedTime",
        description="Estimated duration in milliseconds",
        ge=0,
        example=138000,
    )
    labels: Labels | None = Field(
        None,
        description="Array of labels",
        example=["Regression", "Performance"],
    )
    component: JiraComponent | None = Field(
        None, description="Jira component information"
    )
    folder: FolderLink | None = Field(None, description="Folder information")
    owner: JiraUserLink | None = Field(None, description="Test case owner")
    test_script: TestCaseTestScriptLink | None = Field(
        None, alias="testScript", description="Test script reference"
    )
    custom_fields: CustomFields | None = Field(
        None, alias="customFields", description="Custom field values"
    )
    links: TestCaseLinkList | None = Field(
        None, description="Test case links (issues and web links)"
    )

    model_config = {"populate_by_name": True}


class PagedList(BaseModel):
    """Base traditional pagination response."""

    next: str | None = Field(
        None,
        description="URL for the next page of results",
        format="url",
    )
    start_at: int = Field(
        ...,
        alias="startAt",
        description="Zero-indexed starting position",
        ge=0,
        example=0,
    )
    max_results: int = Field(
        ...,
        alias="maxResults",
        description="Maximum number of results per page",
        ge=0,
        example=10,
    )

    model_config = {"populate_by_name": True}


class TestCaseList(PagedList):
    """Response schema for traditional test cases endpoint (offset-based pagination)."""

    values: list[TestCase] = Field(
        default_factory=list,
        description="List of test cases",
    )
