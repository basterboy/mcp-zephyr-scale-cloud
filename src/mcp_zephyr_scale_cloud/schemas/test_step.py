"""Pydantic models for Zephyr Scale test step entities."""

from pydantic import BaseModel, Field

from .base import Link, PagedResponse
from .common import CustomFields


class TestStepInline(BaseModel):
    """Inline test step definition."""

    description: str = Field(
        ...,
        description="The instruction to be followed",
        example="Attempt to login to the application",
    )
    test_data: str | None = Field(
        None,
        alias="testData",
        description="Any test data required to perform the instruction (optional)",
        example="Username = SmartBear Password = weLoveAtlassian",
    )
    expected_result: str | None = Field(
        None,
        alias="expectedResult",
        description="The expected outcome of executing the instruction",
        example="Login succeeds, web-app redirects to the dashboard view",
    )
    custom_fields: CustomFields | None = Field(None, alias="customFields")
    reflect_ref: str | None = Field(
        None, alias="reflectRef", description="The AI reference. Zephyr only feature"
    )


class TestStepTestCaseParameters(BaseModel):
    """Parameters for test step that delegates to another test case."""

    name: str = Field(..., description="Name of the parameter", example="username")
    type: str = Field(
        ...,
        description="Type of the parameter. Manual inputs or default values",
        example="DEFAULT_VALUE",
    )
    value: str = Field(..., description="Value of the parameter", example="admin")


class TestStepTestCase(Link):
    """Test step that delegates execution to another test case."""

    test_case_key: str = Field(
        ...,
        alias="testCaseKey",
        pattern=r"(.+-T[0-9]+)",
        description="The key of the other test case to delegate execution to",
    )
    parameters: list[TestStepTestCaseParameters] | None = Field(
        None, description="The list of parameters of the call to test step"
    )


class TestStep(BaseModel):
    """A test step instruction."""

    inline: TestStepInline | None = Field(
        None, description="Inline test step definition"
    )
    test_case: TestStepTestCase | None = Field(
        None,
        alias="testCase",
        description="Test step that delegates execution to another test case",
    )

    model_config = {"populate_by_name": True}


class TestStepsList(PagedResponse[TestStep]):
    """Response body when retrieving test steps."""

    values: list[TestStep] = Field(
        default_factory=list, description="The list of test steps"
    )
