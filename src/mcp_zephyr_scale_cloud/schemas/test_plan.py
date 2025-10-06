"""Pydantic schemas for Test Plan operations in Zephyr Scale Cloud."""

from pydantic import BaseModel, Field, field_validator

from .base import PagedResponse
from .common import CustomFields, ProjectLink
from .folder import FolderLink
from .status import StatusLink
from .test_case import IssueLink, JiraUserLink, Labels, WebLink


class TestPlanInput(BaseModel):
    """Schema for creating a test plan."""

    model_config = {"populate_by_name": True}

    project_key: str = Field(
        ...,
        alias="projectKey",
        pattern=r"([A-Z][A-Z_0-9]+)",
        description="Jira project key (e.g., 'PROJ')",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the test plan",
    )
    objective: str | None = Field(
        None,
        description="Objective of the test plan",
    )
    folder_id: int | None = Field(
        None,
        alias="folderId",
        ge=1,
        description="ID of a folder to place the test plan within",
    )
    status_name: str | None = Field(
        None,
        alias="statusName",
        description="Name of the status for the test plan",
    )
    owner_id: str | None = Field(
        None,
        alias="ownerId",
        description="Jira user account ID for owner",
    )
    labels: Labels | None = Field(
        None,
        description="Labels associated with the test plan",
    )
    custom_fields: CustomFields | None = Field(
        None,
        alias="customFields",
        description="Custom fields for the test plan",
    )


class TestPlanTestCycleLink(BaseModel):
    """Schema for a test cycle link within a test plan."""

    model_config = {"populate_by_name": True}

    id: int = Field(..., description="Link ID")
    self_link: str = Field(
        ...,
        alias="self",
        description="Self link URL",
    )
    test_cycle_id: int = Field(
        ...,
        alias="testCycleId",
        description="ID of the linked test cycle",
    )


class TestPlanLinks(BaseModel):
    """Schema for test plan links."""

    model_config = {"populate_by_name": True}

    web_links: list[WebLink] = Field(
        default_factory=list,
        alias="webLinks",
        description="Web links associated with the test plan",
    )
    issues: list[IssueLink] = Field(
        default_factory=list,
        alias="issues",
        description="Issue links associated with the test plan",
    )
    test_cycles: list[TestPlanTestCycleLink] = Field(
        default_factory=list,
        alias="testCycles",
        description="Test cycle links associated with the test plan",
    )


class TestPlan(BaseModel):
    """Schema for a test plan entity."""

    model_config = {"populate_by_name": True}

    id: int = Field(..., description="Test plan ID")
    key: str = Field(
        ...,
        pattern=r".+-P[0-9]+",
        description="Test plan key (e.g., 'PROJ-P123')",
    )
    name: str = Field(..., description="Name of the test plan")
    project: ProjectLink = Field(..., description="Associated project")
    status: StatusLink = Field(..., description="Current status")
    objective: str | None = Field(None, description="Objective of the test plan")
    folder: FolderLink | None = Field(
        None, description="Folder containing the test plan"
    )
    owner: JiraUserLink | None = Field(None, description="Owner of the test plan")
    custom_fields: CustomFields | None = Field(
        None,
        alias="customFields",
        description="Custom fields",
    )
    labels: Labels | None = Field(None, description="Labels")
    links: TestPlanLinks | None = Field(None, description="Associated links")

    @field_validator("key")
    @classmethod
    def validate_key_format(cls, v: str) -> str:
        """Validate test plan key format."""
        if not v or len(v) < 4:  # Minimum: AB-P1
            raise ValueError(
                "Test plan key must follow pattern [PROJECT]-P[NUMBER] "
                "(e.g., 'PROJ-P123')"
            )
        return v


class TestPlanList(PagedResponse[TestPlan]):
    """Schema for paginated test plan list response."""

    model_config = {"populate_by_name": True}

    values: list[TestPlan] = Field(
        default_factory=list,
        description="List of test plans in the current page",
    )


class TestPlanTestCycleLinkInput(BaseModel):
    """Schema for linking a test plan to a test cycle."""

    model_config = {"populate_by_name": True}

    test_cycle_id_or_key: str = Field(
        ...,
        alias="testCycleIdOrKey",
        pattern=r"^([0-9]+|[A-Z][A-Z0-9_]+-R[0-9]+)$",
        description=(
            "The ID or key of the test cycle. "
            "Test cycle keys are of the format [A-Z]+-R[0-9]+"
        ),
    )


class WebLinkInputWithMandatoryDescription(BaseModel):
    """Schema for creating a web link with mandatory description (for test plans)."""

    model_config = {"populate_by_name": True}

    url: str = Field(
        ...,
        description="Web URL to link to",
    )
    description: str = Field(
        ...,
        min_length=1,
        description="Description for the web link (required for test plans)",
    )
