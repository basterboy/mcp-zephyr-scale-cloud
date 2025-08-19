"""Base schemas for Zephyr Scale Cloud API."""

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class BaseEntity(BaseModel):
    """Base model for all Zephyr Scale entities."""

    model_config = ConfigDict(
        # Allow extra fields that might come from API
        extra="allow",
        # Use enum values instead of enum objects
        use_enum_values=True,
        # Validate assignment
        validate_assignment=True,
    )


class Link(BaseModel):
    """Link reference schema."""

    self: str | None = Field(None, description="Self reference URL")


class EntityId(BaseModel):
    """Entity with ID reference."""

    id: int = Field(..., description="Entity ID", ge=1)


class EntityWithLink(EntityId, Link):
    """Entity with both ID and link."""

    pass


class ApiResponse(BaseModel):
    """Base API response schema."""

    success: bool = Field(True, description="Whether the operation was successful")
    message: str | None = Field(None, description="Response message")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Response timestamp"
    )


class ErrorResponse(BaseModel):
    """Error response schema."""

    error_code: int = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: dict[str, Any] | None = Field(None, description="Additional error details")


T = TypeVar("T")


class PagedResponse(BaseModel, Generic[T]):
    """Paged response schema for list endpoints."""

    values: list[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items", ge=0)
    maxResults: int = Field(
        ..., description="Maximum results per page", ge=1, alias="maxResults"
    )
    startAt: int = Field(..., description="Starting index", ge=0, alias="startAt")
    isLast: bool = Field(
        ..., description="Whether this is the last page", alias="isLast"
    )
    next: str | None = Field(None, description="URL for next page")


class CreatedResource(BaseModel):
    """Response for created resources."""

    id: int = Field(..., description="ID of the created resource")
    self: str | None = Field(None, description="URL of the created resource")
    key: str | None = Field(None, description="Key of the created resource")
