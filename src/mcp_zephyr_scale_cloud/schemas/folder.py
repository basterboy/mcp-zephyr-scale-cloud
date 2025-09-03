"""Folder-related Pydantic schemas for Zephyr Scale Cloud API."""

from enum import Enum

from pydantic import BaseModel, Field

from .base import Link, PagedResponse
from .common import ProjectLink


class FolderType(str, Enum):
    """Folder type enumeration."""

    TEST_CASE = "TEST_CASE"
    TEST_PLAN = "TEST_PLAN"
    TEST_CYCLE = "TEST_CYCLE"


class FolderLink(Link):
    """Folder link reference."""

    id: int = Field(..., description="Folder ID", ge=1)


class Folder(BaseModel):
    """Folder response schema."""

    model_config = {"extra": "forbid"}

    id: int = Field(..., description="Folder ID")
    parent_id: int | None = Field(
        None, alias="parentId", description="Parent folder ID"
    )
    name: str = Field(..., min_length=1, max_length=255, description="Folder name")
    index: int = Field(..., ge=0, description="Folder index/position")
    folder_type: FolderType = Field(..., alias="folderType", description="Folder type")
    project: ProjectLink | None = Field(None, description="Project reference")


class FolderList(PagedResponse[Folder]):
    """Paginated list of folders."""

    values: list[Folder] = Field(default_factory=list, description="List of folders")


class CreateFolderRequest(BaseModel):
    """Request schema for creating a folder."""

    model_config = {"extra": "forbid", "populate_by_name": True}

    parent_id: int | None = Field(
        None,
        alias="parentId",
        ge=1,
        description="Folder ID of the parent folder. Must be null for root folders",
    )
    name: str = Field(..., min_length=1, max_length=255, description="Folder name")
    project_key: str = Field(
        ...,
        alias="projectKey",
        pattern=r"^[A-Z][A-Z_0-9]+$",
        description="Jira project key",
    )
    folder_type: FolderType = Field(..., alias="folderType", description="Folder type")
