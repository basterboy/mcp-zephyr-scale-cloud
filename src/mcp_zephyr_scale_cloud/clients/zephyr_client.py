"""Schema-based HTTP client for Zephyr Scale Cloud API."""

import httpx

from ..config import ZephyrConfig
from ..schemas.base import CreatedResource
from ..schemas.folder import (
    CreateFolderRequest,
    Folder,
    FolderList,
    FolderType,
)
from ..schemas.priority import (
    CreatePriorityRequest,
    Priority,
    PriorityList,
    UpdatePriorityRequest,
)
from ..schemas.status import (
    CreateStatusRequest,
    Status,
    StatusList,
    StatusType,
    UpdateStatusRequest,
)
from ..schemas.test_case import IssueLinkInput, TestCase, TestCaseLinkList, WebLinkInput
from ..schemas.test_script import TestScript, TestScriptInput
from ..schemas.test_step import TestStepsInput, TestStepsList
from ..schemas.version import TestCaseVersionList
from ..utils.validation import (
    ValidationResult,
    validate_api_response,
    validate_pagination_params,
)


class ZephyrClient:
    """Schema-based HTTP client for Zephyr Scale Cloud API.

    This client uses Pydantic schemas for request/response validation
    and provides type-safe interactions with the Zephyr Scale Cloud REST API.
    """

    def __init__(self, config: ZephyrConfig):
        self.config = config
        self.headers = {
            "Authorization": f"Bearer {config.api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def healthcheck(self) -> ValidationResult:
        """Check if Zephyr Scale API is accessible.

        Returns:
            ValidationResult with health status
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.config.base_url}/healthcheck",
                    headers=self.headers,
                    timeout=10.0,
                )
                response.raise_for_status()

                # Zephyr Scale healthcheck returns 200 OK with empty body
                if response.status_code == 200:
                    return ValidationResult(True, data={"status": "UP"})
                else:
                    return ValidationResult(
                        False,
                        ["API returned non-200 status"],
                        {"status": "DOWN", "http_status": response.status_code},
                    )

            except httpx.HTTPError as e:
                return ValidationResult(
                    False, [f"Failed to connect to Zephyr Scale Cloud API: {str(e)}"]
                )

    async def get_priorities(
        self, project_key: str | None = None, max_results: int = 50, start_at: int = 0
    ) -> ValidationResult:
        """Get all priorities from Zephyr Scale Cloud.

        Args:
            project_key: Optional Jira project key to filter priorities
            max_results: Maximum number of results to return (default: 50, max: 1000)
            start_at: Zero-indexed starting position (default: 0)

        Returns:
            ValidationResult containing PriorityList or errors
        """
        # Validate pagination parameters
        pagination_validation = validate_pagination_params(max_results, start_at)
        if not pagination_validation:
            return pagination_validation

        params = pagination_validation.data
        if project_key:
            params["projectKey"] = project_key

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.config.base_url}/priorities",
                    headers=self.headers,
                    params=params,
                    timeout=10.0,
                )
                response.raise_for_status()

                # Validate response against schema
                return validate_api_response(response.json(), PriorityList)

            except httpx.HTTPError as e:
                return ValidationResult(
                    False, [f"Failed to retrieve priorities: {str(e)}"]
                )

    async def get_priority(self, priority_id: int) -> ValidationResult:
        """Get a specific priority by ID.

        Args:
            priority_id: The ID of the priority to retrieve

        Returns:
            ValidationResult containing Priority or errors
        """
        if priority_id < 1:
            return ValidationResult(False, ["Priority ID must be a positive integer"])

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.config.base_url}/priorities/{priority_id}",
                    headers=self.headers,
                    timeout=10.0,
                )
                response.raise_for_status()

                # Validate response against schema
                return validate_api_response(response.json(), Priority)

            except httpx.HTTPError as e:
                if hasattr(e, "response") and e.response.status_code == 404:
                    return ValidationResult(
                        False,
                        [
                            f"Priority with ID {priority_id} does not exist or "
                            "you do not have access to it"
                        ],
                    )
                return ValidationResult(
                    False, [f"Failed to retrieve priority {priority_id}: {str(e)}"]
                )

    async def create_priority(self, request: CreatePriorityRequest) -> ValidationResult:
        """Create a new priority.

        Args:
            request: Validated CreatePriorityRequest schema

        Returns:
            ValidationResult containing CreatedResource or errors
        """
        async with httpx.AsyncClient() as client:
            try:
                # Convert Pydantic model to dict, excluding None values
                payload = request.model_dump(exclude_none=True)

                response = await client.post(
                    f"{self.config.base_url}/priorities",
                    headers=self.headers,
                    json=payload,
                    timeout=10.0,
                )
                response.raise_for_status()

                # Validate response against schema
                return validate_api_response(response.json(), CreatedResource)

            except httpx.HTTPError as e:
                return ValidationResult(False, [f"Failed to create priority: {str(e)}"])

    async def update_priority(
        self, priority_id: int, request: UpdatePriorityRequest
    ) -> ValidationResult:
        """Update an existing priority.

        Args:
            priority_id: ID of the priority to update
            request: Validated UpdatePriorityRequest schema

        Returns:
            ValidationResult indicating success or errors
        """
        if priority_id < 1:
            return ValidationResult(False, ["Priority ID must be a positive integer"])

        async with httpx.AsyncClient() as client:
            try:
                # Convert Pydantic model to dict, excluding None values
                payload = request.model_dump(exclude_none=True)

                response = await client.put(
                    f"{self.config.base_url}/priorities/{priority_id}",
                    headers=self.headers,
                    json=payload,
                    timeout=10.0,
                )
                response.raise_for_status()

                # Update returns 200 OK with no body
                return ValidationResult(
                    True,
                    data={
                        "success": True,
                        "message": f"Priority {priority_id} updated successfully",
                    },
                )

            except httpx.HTTPError as e:
                return ValidationResult(
                    False, [f"Failed to update priority {priority_id}: {str(e)}"]
                )

    # Status operations

    async def get_statuses(
        self,
        project_key: str = None,
        status_type: StatusType = None,
        max_results: int = 50,
        start_at: int = 0,
    ) -> ValidationResult:
        """Get all statuses with optional filtering.

        Args:
            project_key: Optional Jira project key filter
            status_type: Optional status type filter
            max_results: Maximum results to return (1-1000, default: 50)
            start_at: Starting position for pagination (default: 0)

        Returns:
            ValidationResult containing StatusList or error messages
        """
        # Validate pagination parameters
        pagination_result = validate_pagination_params(max_results, start_at)
        if not pagination_result.is_valid:
            return pagination_result

        try:
            params = {
                "maxResults": max_results,
                "startAt": start_at,
            }

            if project_key:
                params["projectKey"] = project_key

            if status_type:
                params["statusType"] = status_type.value

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.config.base_url}/statuses",
                    headers=self.headers,
                    params=params,
                    timeout=10.0,
                )

                response.raise_for_status()
                return validate_api_response(response.json(), StatusList)

        except httpx.HTTPError as e:
            return ValidationResult(
                False,
                [f"Failed to get statuses: {str(e)}"],
            )

    async def get_status(self, status_id: int) -> ValidationResult:
        """Get a specific status by ID.

        Args:
            status_id: The ID of the status to retrieve

        Returns:
            ValidationResult containing Status or error messages
        """
        if status_id < 1:
            return ValidationResult(False, ["Status ID must be a positive integer"])

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.config.base_url}/statuses/{status_id}",
                    headers=self.headers,
                    timeout=10.0,
                )

                response.raise_for_status()
                return validate_api_response(response.json(), Status)

        except httpx.HTTPError as e:
            if hasattr(e, "response") and e.response.status_code == 404:
                return ValidationResult(
                    False,
                    [
                        f"Status with ID {status_id} does not exist or "
                        "you do not have access to it"
                    ],
                )
            return ValidationResult(
                False,
                [f"Failed to get status {status_id}: {str(e)}"],
            )

    async def create_status(self, request: CreateStatusRequest) -> ValidationResult:
        """Create a new status.

        Args:
            request: CreateStatusRequest with status details

        Returns:
            ValidationResult containing CreatedResource or error messages
        """
        try:
            # Convert to dict for API call, excluding None values
            request_data = request.model_dump(exclude_none=True, by_alias=True)

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.config.base_url}/statuses",
                    headers=self.headers,
                    json=request_data,
                    timeout=10.0,
                )

                response.raise_for_status()
                return validate_api_response(response.json(), CreatedResource)

        except httpx.HTTPError as e:
            return ValidationResult(
                False,
                [f"Failed to create status: {str(e)}"],
            )

    async def update_status(
        self, status_id: int, request: UpdateStatusRequest
    ) -> ValidationResult:
        """Update an existing status.

        Args:
            status_id: The ID of the status to update
            request: UpdateStatusRequest with updated status details

        Returns:
            ValidationResult indicating success or error messages
        """
        if status_id < 1:
            return ValidationResult(False, ["Status ID must be a positive integer"])

        try:
            # Convert to dict for API call, excluding None values
            request_data = request.model_dump(exclude_none=True, by_alias=True)

            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.config.base_url}/statuses/{status_id}",
                    headers=self.headers,
                    json=request_data,
                    timeout=10.0,
                )

                response.raise_for_status()

                # Update returns 200 OK with no body
                return ValidationResult(
                    True,
                    data={
                        "success": True,
                        "message": f"Status {status_id} updated successfully",
                    },
                )

        except httpx.HTTPError as e:
            if hasattr(e, "response") and e.response.status_code == 404:
                return ValidationResult(
                    False,
                    [
                        f"Status with ID {status_id} does not exist or "
                        "you do not have access to it"
                    ],
                )
            return ValidationResult(
                False,
                [f"Failed to update status {status_id}: {str(e)}"],
            )

    # Folder operations

    async def get_folders(
        self,
        project_key: str | None = None,
        folder_type: FolderType | None = None,
        max_results: int = 10,
        start_at: int = 0,
    ) -> ValidationResult:
        """Get folders with optional filtering.

        Args:
            project_key: Optional project key filter
            folder_type: Optional folder type filter
            max_results: Maximum number of results (1-1000, default 10)
            start_at: Starting position for pagination (default 0)

        Returns:
            ValidationResult with FolderList data or error messages
        """
        # Validate pagination parameters
        pagination_result = validate_pagination_params(max_results, start_at)
        if not pagination_result:
            return pagination_result

        try:
            # Build query parameters
            params = {
                "maxResults": max_results,
                "startAt": start_at,
            }

            if project_key:
                params["projectKey"] = project_key

            if folder_type:
                params["folderType"] = folder_type.value

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.config.base_url}/folders",
                    headers=self.headers,
                    params=params,
                    timeout=10.0,
                )

                response.raise_for_status()
                response_data = response.json()

                # Validate and parse response
                return validate_api_response(response_data, FolderList)

        except httpx.HTTPError as e:
            return ValidationResult(
                False,
                [f"Failed to get folders: {str(e)}"],
            )

    async def get_folder(self, folder_id: int) -> ValidationResult:
        """Get a specific folder by ID.

        Args:
            folder_id: Folder ID to retrieve

        Returns:
            ValidationResult with Folder data or error messages
        """
        if folder_id < 1:
            return ValidationResult(False, ["Folder ID must be a positive integer"])

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.config.base_url}/folders/{folder_id}",
                    headers=self.headers,
                    timeout=10.0,
                )

                response.raise_for_status()
                response_data = response.json()

                # Validate and parse response
                return validate_api_response(response_data, Folder)

        except httpx.HTTPError as e:
            if hasattr(e, "response") and e.response.status_code == 404:
                return ValidationResult(
                    False,
                    [
                        f"Folder with ID {folder_id} does not exist or "
                        "you do not have access to it"
                    ],
                )
            return ValidationResult(
                False,
                [f"Failed to get folder {folder_id}: {str(e)}"],
            )

    async def create_folder(self, request: CreateFolderRequest) -> ValidationResult:
        """Create a new folder.

        Args:
            request: CreateFolderRequest with folder details

        Returns:
            ValidationResult with CreatedResource data or error messages
        """
        try:
            # Convert to dict for API call, using aliases for camelCase
            request_data = request.model_dump(exclude_none=True, by_alias=True)

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.config.base_url}/folders",
                    headers=self.headers,
                    json=request_data,
                    timeout=10.0,
                )

                response.raise_for_status()
                response_data = response.json()

                # Validate and parse response
                return validate_api_response(response_data, CreatedResource)

        except httpx.HTTPError as e:
            return ValidationResult(
                False,
                [f"Failed to create folder: {str(e)}"],
            )

    async def get_test_steps(
        self,
        test_case_key: str,
        max_results: int = 10,
        start_at: int = 0,
    ) -> "ValidationResult[TestStepsList]":
        """
        Get test steps for a specific test case.

        Args:
            test_case_key: The key of the test case (format: [A-Z]+-T[0-9]+)
            max_results: Maximum number of results to return (default: 10, max: 1000)
            start_at: Zero-indexed starting position (default: 0)

        Returns:
            ValidationResult with TestStepsList data or error messages
        """
        # Validate pagination parameters
        pagination_validation = validate_pagination_params(max_results, start_at)
        if not pagination_validation.is_valid:
            return ValidationResult(False, pagination_validation.errors)

        try:
            # Build query parameters
            params = {
                "maxResults": max_results,
                "startAt": start_at,
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.config.base_url}/testcases/{test_case_key}/teststeps",
                    headers=self.headers,
                    params=params,
                    timeout=10.0,
                )

                response.raise_for_status()
                response_data = response.json()

                # Validate and parse response
                return validate_api_response(response_data, TestStepsList)

        except httpx.HTTPError as e:
            return ValidationResult(
                False,
                [f"Failed to get test steps for test case {test_case_key}: {str(e)}"],
            )

    async def create_test_steps(
        self,
        test_case_key: str,
        test_steps_input: TestStepsInput,
    ) -> "ValidationResult[CreatedResource]":
        """
        Create test steps for a specific test case.

        Args:
            test_case_key: The key of the test case (format: [A-Z]+-T[0-9]+)
            test_steps_input: TestStepsInput with mode and list of test steps

        Returns:
            ValidationResult with CreatedResource data or error messages
        """
        try:
            # Convert to dict for API call, using aliases for camelCase
            request_data = test_steps_input.model_dump(exclude_none=True, by_alias=True)

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.config.base_url}/testcases/{test_case_key}/teststeps",
                    headers=self.headers,
                    json=request_data,
                    timeout=10.0,
                )

                response.raise_for_status()
                response_data = response.json()

                # Validate and parse response
                return validate_api_response(response_data, CreatedResource)

        except httpx.HTTPError as e:
            return ValidationResult(
                False,
                [
                    f"Failed to create test steps for test case "
                    f"{test_case_key}: {str(e)}"
                ],
            )

    async def get_test_script(
        self, test_case_key: str
    ) -> "ValidationResult[TestScript]":
        """
        Get test script for a specific test case.

        Args:
            test_case_key: The key of the test case (format: [A-Z]+-T[0-9]+)

        Returns:
            ValidationResult with TestScript data or error messages
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.config.base_url}/testcases/{test_case_key}/testscript",
                    headers=self.headers,
                    timeout=10.0,
                )

                response.raise_for_status()
                response_data = response.json()

                # Validate and parse response
                return validate_api_response(response_data, TestScript)

        except httpx.HTTPError as e:
            return ValidationResult(
                False,
                [f"Failed to get test script for test case {test_case_key}: {str(e)}"],
            )

    async def create_test_script(
        self,
        test_case_key: str,
        test_script_input: TestScriptInput,
    ) -> "ValidationResult[CreatedResource]":
        """
        Create or update test script for a specific test case.

        Args:
            test_case_key: The key of the test case (format: [A-Z]+-T[0-9]+)
            test_script_input: TestScriptInput with type and text

        Returns:
            ValidationResult with CreatedResource data or error messages
        """
        try:
            # Convert to dict for API call, using aliases for camelCase
            request_data = test_script_input.model_dump(
                exclude_none=True, by_alias=True
            )

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.config.base_url}/testcases/{test_case_key}/testscript",
                    headers=self.headers,
                    json=request_data,
                    timeout=10.0,
                )

                response.raise_for_status()
                response_data = response.json()

                # Validate and parse response
                return validate_api_response(response_data, CreatedResource)

        except httpx.HTTPError as e:
            return ValidationResult(
                False,
                [
                    f"Failed to create test script for test case "
                    f"{test_case_key}: {str(e)}"
                ],
            )

    async def get_test_case(self, test_case_key: str) -> "ValidationResult[TestCase]":
        """
        Get detailed information for a specific test case.

        Args:
            test_case_key: The key of the test case (format: [A-Z]+-T[0-9]+)

        Returns:
            ValidationResult with TestCase data or error messages
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.config.base_url}/testcases/{test_case_key}",
                    headers=self.headers,
                    timeout=10.0,
                )

                response.raise_for_status()
                response_data = response.json()

                # Validate and parse response
                return validate_api_response(response_data, TestCase)

        except httpx.HTTPError as e:
            return ValidationResult(
                False,
                [f"Failed to get test case {test_case_key}: {str(e)}"],
            )

    async def get_test_case_versions(
        self,
        test_case_key: str,
        max_results: int = 10,
        start_at: int = 0,
    ) -> "ValidationResult[TestCaseVersionList]":
        """
        Get all versions for a test case.

        Args:
            test_case_key: The key of the test case (format: [A-Z]+-T[0-9]+)
            max_results: Maximum number of results to return (default: 10, max: 1000)
            start_at: Zero-indexed starting position (default: 0)

        Returns:
            ValidationResult with TestCaseVersionList data or error messages
        """
        try:
            # Validate pagination parameters
            validation_result = validate_pagination_params(max_results, start_at)
            if not validation_result.is_valid:
                return ValidationResult(False, validation_result.errors)

            params = {
                "maxResults": max_results,
                "startAt": start_at,
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.config.base_url}/testcases/{test_case_key}/versions",
                    headers=self.headers,
                    params=params,
                    timeout=10.0,
                )

                response.raise_for_status()
                response_data = response.json()

                # Validate and parse response
                return validate_api_response(response_data, TestCaseVersionList)

        except httpx.HTTPError as e:
            return ValidationResult(
                False,
                [f"Failed to get versions for test case {test_case_key}: {str(e)}"],
            )

    async def get_test_case_version(
        self, test_case_key: str, version: int
    ) -> "ValidationResult[TestCase]":
        """
        Get a specific version of a test case.

        Args:
            test_case_key: The key of the test case (format: [A-Z]+-T[0-9]+)
            version: Version number to retrieve

        Returns:
            ValidationResult with TestCase data or error messages
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.config.base_url}/testcases/{test_case_key}/versions/{version}",
                    headers=self.headers,
                    timeout=10.0,
                )

                response.raise_for_status()
                response_data = response.json()

                # Validate and parse response
                return validate_api_response(response_data, TestCase)

        except httpx.HTTPError as e:
            return ValidationResult(
                False,
                [
                    f"Failed to get version {version} for test case "
                    f"{test_case_key}: {str(e)}"
                ],
            )

    async def get_test_case_links(
        self, test_case_key: str
    ) -> "ValidationResult[TestCaseLinkList]":
        """
        Get all links (issues + web links) for a test case.

        Args:
            test_case_key: The key of the test case (format: [A-Z]+-T[0-9]+)

        Returns:
            ValidationResult with TestCaseLinkList data or error messages
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.config.base_url}/testcases/{test_case_key}/links",
                    headers=self.headers,
                    timeout=10.0,
                )

                response.raise_for_status()
                response_data = response.json()

                # Validate and parse response
                return validate_api_response(response_data, TestCaseLinkList)

        except httpx.HTTPError as e:
            return ValidationResult(
                False,
                [f"Failed to get links for test case {test_case_key}: {str(e)}"],
            )

    async def create_test_case_issue_link(
        self, test_case_key: str, issue_link_input: IssueLinkInput
    ) -> "ValidationResult[CreatedResource]":
        """
        Create a link between a test case and a Jira issue.

        Args:
            test_case_key: The key of the test case (format: [A-Z]+-T[0-9]+)
            issue_link_input: Issue link input data

        Returns:
            ValidationResult with CreatedResource data or error messages
        """
        try:
            # Convert to dict for API request
            request_data = issue_link_input.model_dump(by_alias=True)

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.config.base_url}/testcases/{test_case_key}/links/issues",
                    headers=self.headers,
                    json=request_data,
                    timeout=10.0,
                )

                response.raise_for_status()
                response_data = response.json()

                # Validate and parse response
                return validate_api_response(response_data, CreatedResource)

        except httpx.HTTPError as e:
            return ValidationResult(
                False,
                [
                    f"Failed to create issue link for test case "
                    f"{test_case_key}: {str(e)}"
                ],
            )

    async def create_test_case_web_link(
        self, test_case_key: str, web_link_input: WebLinkInput
    ) -> "ValidationResult[CreatedResource]":
        """
        Create a link between a test case and a web URL.

        Args:
            test_case_key: The key of the test case (format: [A-Z]+-T[0-9]+)
            web_link_input: Web link input data

        Returns:
            ValidationResult with CreatedResource data or error messages
        """
        try:
            # Convert to dict for API request
            request_data = web_link_input.model_dump(by_alias=True)

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.config.base_url}/testcases/{test_case_key}/links/weblinks",
                    headers=self.headers,
                    json=request_data,
                    timeout=10.0,
                )

                response.raise_for_status()
                response_data = response.json()

                # Validate and parse response
                return validate_api_response(response_data, CreatedResource)

        except httpx.HTTPError as e:
            return ValidationResult(
                False,
                [
                    f"Failed to create web link for test case "
                    f"{test_case_key}: {str(e)}"
                ],
            )
