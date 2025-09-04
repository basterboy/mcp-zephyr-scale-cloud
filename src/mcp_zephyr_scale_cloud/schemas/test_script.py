"""Pydantic models for Zephyr Scale test script entities."""

from enum import Enum

from pydantic import BaseModel, Field

# EntityId type definition for test scripts
EntityId = int


class TestScriptType(str, Enum):
    """Test script type."""

    PLAIN = "plain"
    BDD = "bdd"


class TestScriptInput(BaseModel):
    """Request body for creating test scripts."""

    type: TestScriptType = Field(
        ...,
        description="Test script type: plain text or BDD format",
        example="plain",
    )
    text: str = Field(
        ...,
        description="The test script content (empty string if no script exists)",
        example="e.g. Attempt to login to the application",
    )

    model_config = {"populate_by_name": True}


class TestScript(TestScriptInput):
    """Response body when retrieving test scripts."""

    id: EntityId = Field(
        ...,
        description="The unique identifier of the test script",
        example=1,
        ge=1,
    )

    model_config = {"populate_by_name": True}
