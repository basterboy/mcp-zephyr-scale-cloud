"""Common schemas shared across entities."""

from pydantic import Field

from .base import BaseEntity, EntityWithLink


class Project(EntityWithLink):
    """Project schema."""

    key: str | None = Field(None, description="Project key", pattern=r"[A-Z][A-Z_0-9]+")
    name: str | None = Field(None, description="Project name")


class ProjectLink(EntityWithLink):
    """Project link reference."""

    pass


class OptionValue(BaseEntity):
    """Base schema for option values (priorities, statuses, etc.)."""

    id: int = Field(..., description="Option ID", ge=1)
    name: str = Field(..., description="Option name", min_length=1, max_length=255)
    description: str | None = Field(
        None, description="Option description", min_length=1, max_length=255
    )
    index: int = Field(..., description="Display order index", ge=0)
    project: ProjectLink = Field(..., description="Associated project")


class EntityColor(BaseEntity):
    """Color field schema."""

    color: str | None = Field(
        None,
        description="Hex color code (3 or 6 characters)",
        pattern=r"^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$",
        examples=["#FFF", "#FFFFFF", "#FF0000"],
    )
