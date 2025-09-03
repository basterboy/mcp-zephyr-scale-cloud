"""Priority-related schemas for Zephyr Scale Cloud API."""

from pydantic import Field, field_validator

from .base import BaseEntity, EntityWithLink, PagedResponse
from .common import OptionValue, ProjectLink


class PriorityLink(EntityWithLink):
    """Priority link reference."""

    pass


class Priority(OptionValue):
    """Priority schema matching Zephyr Scale Cloud API."""

    color: str | None = Field(
        None,
        description="Priority color in hex format (3 or 6 characters)",
        pattern=r"^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$",
    )
    default: bool = Field(False, description="Whether this is the default priority")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate priority name."""
        if not v or not v.strip():
            raise ValueError("Priority name cannot be empty")
        return v.strip()

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str | None) -> str | None:
        """Validate color format."""
        if v and not v.startswith("#"):
            raise ValueError("Color must be in hex format (e.g., '#FFF' or '#FF0000')")
        return v


class PriorityList(PagedResponse[Priority]):
    """Paged list of priorities."""

    pass


class CreatePriorityRequest(BaseEntity):
    """Request schema for creating a priority."""

    projectKey: str = Field(
        ...,
        description="Jira project key",
        pattern=r"[A-Z][A-Z_0-9]+",
        examples=["PROJ", "TEST"],
        alias="projectKey",
    )
    name: str = Field(..., description="Priority name", min_length=1, max_length=255)
    description: str | None = Field(
        None, description="Priority description", min_length=1, max_length=255
    )
    color: str | None = Field(
        None,
        description="Priority color in hex format (3 or 6 characters)",
        pattern=r"^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$",
        examples=["#FFF", "#FF0000"],
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and clean priority name."""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Priority name cannot be empty")
        return cleaned

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        """Validate and clean description."""
        return v.strip() if v else None


class UpdatePriorityRequest(BaseEntity):
    """Request schema for updating a priority."""

    id: int = Field(..., description="Priority ID to update", ge=1)
    project: ProjectLink = Field(..., description="Project reference")
    name: str = Field(
        ..., description="Updated priority name", min_length=1, max_length=255
    )
    description: str | None = Field(
        None, description="Updated priority description", min_length=1, max_length=255
    )
    index: int = Field(..., description="Priority display order", ge=0)
    default: bool = Field(..., description="Whether this is the default priority")
    color: str | None = Field(
        None,
        description="Updated priority color in hex format (3 or 6 characters)",
        pattern=r"^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and clean priority name."""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Priority name cannot be empty")
        return cleaned

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        """Validate and clean description."""
        return v.strip() if v else None
