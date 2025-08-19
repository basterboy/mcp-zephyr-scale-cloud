"""Project-related schemas for Zephyr Scale Cloud API."""

from pydantic import Field

from .base import EntityWithLink


class Project(EntityWithLink):
    """Project schema."""

    key: str | None = Field(
        None,
        description="Project key",
        pattern=r"[A-Z][A-Z_0-9]+",
        examples=["PROJ", "TEST"],
    )
    name: str | None = Field(None, description="Project name", max_length=255)
    description: str | None = Field(None, description="Project description")


class ProjectLink(EntityWithLink):
    """Project link reference schema."""

    pass
