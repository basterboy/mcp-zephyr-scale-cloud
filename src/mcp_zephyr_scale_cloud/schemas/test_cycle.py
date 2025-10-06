"""Pydantic models for Zephyr Scale test cycle entities."""

from typing import Any

from pydantic import BaseModel, Field

from .base import PagedResponse
from .common import CustomFields, ProjectLink
from .folder import FolderLink
from .status import StatusLink

# Type aliases
EntityId = int


class JiraProjectVersion(BaseModel):
    """Jira project version reference."""

    model_config = {"populate_by_name": True}

    id: int = Field(..., description="Version ID", ge=1, example=10000)
    self: str | None = Field(
        None,
        description="Self reference URL",
        example="https://<jira-instance>.atlassian.net/rest/api/2/version/10000",
    )


class JiraUserLink(BaseModel):
    """Jira user reference link."""

    model_config = {"populate_by_name": True}

    account_id: str | None = Field(
        None,
        alias="accountId",
        description="Jira user account ID",
        example="712020:b231ae42-7619-42b4-9cd8-a83e0cdc00ad",
    )
    self: str | None = Field(
        None,
        description="Self reference URL",
    )


class TestCycleInput(BaseModel):
    """Input schema for creating test cycles."""

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
        description="The test cycle name",
        min_length=1,
        example="Sprint 1 Regression Test Cycle",
    )
    description: str | None = Field(
        None,
        description="Description outlining the scope",
        example="Test cycle for sprint 1 regression testing",
    )
    planned_start_date: str | None = Field(
        None,
        alias="plannedStartDate",
        description=(
            "Planned start date of the test cycle. " "Format: yyyy-MM-dd'T'HH:mm:ss'Z'"
        ),
        example="2018-05-19T13:15:13Z",
    )
    planned_end_date: str | None = Field(
        None,
        alias="plannedEndDate",
        description=(
            "The planned end date of the test cycle. "
            "Format: yyyy-MM-dd'T'HH:mm:ss'Z'"
        ),
        example="2018-05-20T13:15:13Z",
    )
    jira_project_version: int | None = Field(
        None,
        alias="jiraProjectVersion",
        description="ID of the version from Jira",
        ge=1,
        example=10000,
    )
    status_name: str | None = Field(
        None,
        alias="statusName",
        description="The status name (defaults to default status if not specified)",
        max_length=255,
        min_length=1,
        example="Not Executed",
    )
    folder_id: int | None = Field(
        None,
        alias="folderId",
        description="ID of a folder to place the test cycle within",
        ge=1,
        example=12345,
    )
    owner_id: str | None = Field(
        None,
        alias="ownerId",
        description="Jira user account ID for the test cycle owner",
        example="712020:b231ae42-7619-42b4-9cd8-a83e0cdc00ad",
    )
    custom_fields: dict[str, Any] | None = Field(
        None,
        alias="customFields",
        description="Custom fields for the test cycle",
        example={"Environment": "Production", "Release": "v1.0"},
    )


class TestCycle(BaseModel):
    """Test cycle entity from Zephyr Scale."""

    model_config = {"populate_by_name": True}

    # Required fields
    id: EntityId = Field(..., description="Test cycle ID", ge=1)
    key: str = Field(
        ...,
        description="Test cycle key",
        pattern=r".+-[R|C][0-9]+",
        example="PROJ-R40",
    )
    name: str = Field(
        ...,
        description="Test cycle name",
        min_length=1,
        example="Sprint 1 Regression Test Cycle",
    )
    project: ProjectLink = Field(..., description="Project information")
    status: StatusLink = Field(..., description="Status information")

    # Optional fields
    jira_project_version: JiraProjectVersion | None = Field(
        None,
        alias="jiraProjectVersion",
        description="Jira project version information",
    )
    folder: FolderLink | None = Field(None, description="Folder information")
    description: str | None = Field(
        None,
        description="Description outlining the scope",
        example="Test cycle for sprint 1 regression testing",
    )
    planned_start_date: str | None = Field(
        None,
        alias="plannedStartDate",
        description="Planned start date",
        example="2018-05-19T13:15:13Z",
    )
    planned_end_date: str | None = Field(
        None,
        alias="plannedEndDate",
        description="Planned end date",
        example="2018-05-20T13:15:13Z",
    )
    owner: JiraUserLink | None = Field(None, description="Test cycle owner")
    custom_fields: CustomFields | None = Field(
        None, alias="customFields", description="Custom field values"
    )
    links: "TestCycleLinkList | None" = Field(
        None, description="Links associated with the test cycle"
    )


class IssueLink(BaseModel):
    """Issue link entity."""

    model_config = {"populate_by_name": True}

    id: int = Field(..., description="Link ID", ge=1)
    issue_id: int = Field(
        ..., alias="issueId", description="Jira issue ID", ge=1, example=10000
    )
    self: str | None = Field(None, description="Self reference URL")


class WebLink(BaseModel):
    """Web link entity."""

    model_config = {"populate_by_name": True}

    id: int = Field(..., description="Link ID", ge=1)
    url: str = Field(
        ..., description="The web link URL", example="https://atlassian.com"
    )
    description: str | None = Field(
        None, description="The link description", example="A link to atlassian.com"
    )
    self: str | None = Field(None, description="Self reference URL")


class TestCycleLinkList(BaseModel):
    """List of links for a test cycle."""

    model_config = {"populate_by_name": True}

    issues: list[IssueLink] = Field(
        default_factory=list, alias="issueLinks", description="List of issue links"
    )
    web_links: list[WebLink] = Field(
        default_factory=list,
        alias="webLinks",
        description="List of web links",
    )


class TestCycleList(PagedResponse[TestCycle]):
    """Paged list of test cycles."""

    model_config = {"populate_by_name": True}

    values: list[TestCycle] = Field(..., description="The list of test cycles")
