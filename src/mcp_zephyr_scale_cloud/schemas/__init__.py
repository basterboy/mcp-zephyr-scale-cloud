"""Pydantic schemas for Zephyr Scale Cloud API entities."""

from .base import (
    ApiResponse,
    BaseEntity,
    CreatedResource,
    EntityId,
    EntityWithLink,
    ErrorResponse,
    Link,
    PagedResponse,
)
from .common import (
    CustomFields,
    EntityColor,
    OptionValue,
    Project,
    ProjectLink,
)
from .folder import (
    CreateFolderRequest,
    Folder,
    FolderLink,
    FolderList,
    FolderType,
)
from .priority import (
    CreatePriorityRequest,
    Priority,
    PriorityLink,
    PriorityList,
    UpdatePriorityRequest,
)
from .status import (
    CreateStatusRequest,
    Status,
    StatusLink,
    StatusList,
    StatusType,
    UpdateStatusRequest,
)
from .test_case import (
    IssueLink,
    JiraComponent,
    JiraUserLink,
    TestCase,
    TestCaseLinkList,
    TestCaseTestScriptLink,
    WebLink,
)
from .test_script import (
    TestScript,
    TestScriptInput,
    TestScriptType,
)
from .test_step import (
    TestStep,
    TestStepInline,
    TestStepsInput,
    TestStepsList,
    TestStepsMode,
    TestStepTestCase,
    TestStepTestCaseParameters,
)
from .version import (
    TestCaseVersionLink,
    TestCaseVersionList,
)

__all__ = [
    "BaseEntity",
    "Link",
    "EntityId",
    "EntityWithLink",
    "ApiResponse",
    "PagedResponse",
    "ErrorResponse",
    "CreatedResource",
    "Folder",
    "FolderLink",
    "FolderList",
    "CreateFolderRequest",
    "FolderType",
    "Priority",
    "PriorityLink",
    "PriorityList",
    "CreatePriorityRequest",
    "UpdatePriorityRequest",
    "CreateStatusRequest",
    "Status",
    "StatusLink",
    "StatusList",
    "StatusType",
    "UpdateStatusRequest",
    "Project",
    "ProjectLink",
    "OptionValue",
    "EntityColor",
    "CustomFields",
    "IssueLink",
    "JiraComponent",
    "JiraUserLink",
    "TestCase",
    "TestCaseLinkList",
    "TestCaseTestScriptLink",
    "WebLink",
    "TestScript",
    "TestScriptInput",
    "TestScriptType",
    "TestStep",
    "TestStepInline",
    "TestStepsInput",
    "TestStepsList",
    "TestStepsMode",
    "TestStepTestCase",
    "TestStepTestCaseParameters",
    "TestCaseVersionLink",
    "TestCaseVersionList",
]
