"""Pydantic schemas for Zephyr Scale Status operations."""

from enum import Enum

from pydantic import BaseModel, Field, field_validator

from .base import EntityWithLink, PagedResponse
from .common import ProjectLink


class StatusType(str, Enum):
    """Valid status types in Zephyr Scale."""

    TEST_CASE = "TEST_CASE"
    TEST_PLAN = "TEST_PLAN"
    TEST_CYCLE = "TEST_CYCLE"
    TEST_EXECUTION = "TEST_EXECUTION"


class StatusLink(EntityWithLink):
    """Status link reference."""

    pass


class Status(BaseModel):
    """Status schema based on actual API response format."""

    model_config = {"extra": "forbid"}

    id: int = Field(..., description="Status ID", ge=1)
    project: ProjectLink = Field(..., description="Project this status belongs to")
    name: str = Field(..., description="Status name", min_length=1, max_length=255)
    description: str | None = Field(
        None, description="Status description", max_length=255
    )
    index: int = Field(..., description="Display order index", ge=0)
    color: str | None = Field(None, description="Color in hexadecimal format")
    archived: bool = Field(default=False, description="Whether status is archived")
    default: bool = Field(
        default=False, description="Whether this is the default status"
    )

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str | None) -> str | None:
        """Validate color format if provided."""
        if v is None:
            return v
        if not v.startswith("#") or len(v) not in [4, 7]:
            raise ValueError("Color must be in format #RGB or #RRGGBB")
        return v


class StatusList(PagedResponse[Status]):
    """Paged list of statuses."""

    values: list[Status] = Field(default_factory=list, description="List of statuses")


class CreateStatusRequest(BaseModel):
    """Request schema for creating a new status."""

    model_config = {"extra": "forbid", "populate_by_name": True}

    project_key: str = Field(
        ...,
        description="Jira project key",
        pattern=r"([A-Z][A-Z_0-9]+)",
        alias="projectKey",
    )
    name: str = Field(..., description="Status name", min_length=1, max_length=255)
    type: StatusType = Field(..., description="Status type")
    description: str | None = Field(
        None, description="Status description", max_length=255
    )
    color: str | None = Field(None, description="Color in hexadecimal format")

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str | None) -> str | None:
        """Validate color format if provided."""
        if v is None:
            return v
        if not v.startswith("#") or len(v) not in [4, 7]:
            raise ValueError("Color must be in format #RGB or #RRGGBB")
        return v


class UpdateStatusRequest(BaseModel):
    """Request schema for updating an existing status."""

    model_config = {"extra": "forbid", "populate_by_name": True}

    id: int = Field(..., description="Status ID", ge=1)
    project: ProjectLink = Field(..., description="Project this status belongs to")
    name: str = Field(..., description="Status name", min_length=1, max_length=255)
    description: str | None = Field(
        None, description="Status description", max_length=255
    )
    index: int = Field(..., description="Display order index", ge=0)
    archived: bool = Field(..., description="Whether status is archived")
    default: bool = Field(..., description="Whether this is the default status")
    color: str | None = Field(None, description="Color in hexadecimal format")

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str | None) -> str | None:
        """Validate color format if provided."""
        if v is None:
            return v
        if not v.startswith("#") or len(v) not in [4, 7]:
            raise ValueError("Color must be in format #RGB or #RRGGBB")
        return v
