"""Version-related schemas for Zephyr Scale Cloud API."""

from pydantic import Field

from .base import Link, PagedResponse


class TestCaseVersionLink(Link):
    """Test case version link reference."""

    id: int = Field(..., description="Version ID", ge=1)


class TestCaseVersionList(PagedResponse[TestCaseVersionLink]):
    """Paginated list of test case versions."""

    pass
