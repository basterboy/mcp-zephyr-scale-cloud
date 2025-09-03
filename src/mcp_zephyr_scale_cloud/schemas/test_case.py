"""Pydantic models for Zephyr Scale test case entities."""

from datetime import datetime

from pydantic import BaseModel, Field

from .base import Link
from .common import CustomFields, ProjectLink
from .folder import FolderLink
from .priority import PriorityLink
from .status import StatusLink

# Type aliases for simple types
EntityId = int
Labels = list[str]


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
