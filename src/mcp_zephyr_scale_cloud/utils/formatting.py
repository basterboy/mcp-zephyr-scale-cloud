"""Formatting utilities for MCP tool outputs."""

from typing import Any

from ..schemas.folder import Folder, FolderList
from ..schemas.priority import Priority, PriorityList
from ..schemas.status import Status, StatusList
from ..schemas.test_script import TestScript
from ..schemas.test_step import TestStep, TestStepsList


def format_priority_display(priority: Priority) -> str:
    """Format a single priority for display.

    Args:
        priority: Priority schema instance

    Returns:
        Formatted priority string
    """
    output = f"**{priority.name}** (ID: {priority.id})\n"

    if priority.description:
        output += f"   📝 {priority.description}\n"

    output += f"   📊 Index: {priority.index}"

    if priority.default:
        output += " ⭐ (Default)"

    if priority.color:
        output += f" 🎨 {priority.color}"

    output += f"\n   🏗️ Project: {priority.project.id}\n"

    return output


def format_priority_list(
    priority_list: PriorityList, project_key: str | None = None
) -> str:
    """Format a list of priorities for display.

    Args:
        priority_list: PriorityList schema instance
        project_key: Optional project key for context

    Returns:
        Formatted priority list string
    """
    if not priority_list.values:
        filter_msg = f" for project {project_key}" if project_key else ""
        return f"📋 No priorities found{filter_msg}."

    output = (
        f"📋 **Priorities** ({len(priority_list.values)} of {priority_list.total})\n"
    )

    if project_key:
        output += f"🏷️ Project: {project_key}\n"

    output += "\n"

    for priority in priority_list.values:
        output += format_priority_display(priority) + "\n"

    return output.strip()


def format_priority_details(priority: Priority) -> str:
    """Format detailed priority information.

    Args:
        priority: Priority schema instance

    Returns:
        Formatted priority details string
    """
    output = "📋 **Priority Details**\n\n"
    output += f"**{priority.name}** (ID: {priority.id})\n"

    if priority.description:
        output += f"📝 **Description:** {priority.description}\n"

    output += f"📊 **Index:** {priority.index}\n"

    if priority.default:
        output += "⭐ **Default Priority:** Yes\n"

    if priority.color:
        output += f"🎨 **Color:** {priority.color}\n"

    output += f"🏗️ **Project:** {priority.project.id}\n"

    return output


def format_success_message(
    operation: str, entity_type: str, entity_id: Any | None = None, **details
) -> str:
    """Format a success message.

    Args:
        operation: Operation performed (e.g., "Created", "Updated")
        entity_type: Type of entity (e.g., "Priority", "Test Case")
        entity_id: Optional entity ID
        **details: Additional details to include

    Returns:
        Formatted success message
    """
    output = f"✅ **{entity_type} {operation} Successfully!**\n\n"

    if entity_id:
        output += f"🆔 **ID:** {entity_id}\n"

    for key, value in details.items():
        if value is not None:
            # Convert snake_case to Title Case
            label = key.replace("_", " ").title()
            # Add appropriate emoji for common fields
            emoji = {
                "name": "📋",
                "project": "🏷️",
                "project_key": "🏷️",
                "description": "📝",
                "color": "🎨",
                "index": "📊",
                "url": "🔗",
                "default": "⭐",
            }.get(key.lower(), "📄")

            if key.lower() == "default" and value:
                output += f"{emoji} **Default Priority:** Yes\n"
            else:
                output += f"{emoji} **{label}:** {value}\n"

    return output


def format_error_message(operation: str, error: str, details: str | None = None) -> str:
    """Format an error message.

    Args:
        operation: Operation that failed
        error: Main error message
        details: Optional additional details

    Returns:
        Formatted error message
    """
    output = f"❌ ERROR: {error}"

    if details:
        output += f"\n🔍 Details: {details}"

    return output


def format_validation_errors(errors: list[str]) -> str:
    """Format validation errors.

    Args:
        errors: List of validation error messages

    Returns:
        Formatted validation errors string
    """
    if not errors:
        return ""

    output = "❌ **Validation Errors:**\n"
    for error in errors:
        output += f"   • {error}\n"

    return output.strip()


def format_status_display(status: Status) -> str:
    """Format a single status for display.

    Args:
        status: Status schema instance

    Returns:
        Formatted status string
    """
    output = f"**{status.name}** (ID: {status.id})\n"

    if status.description:
        output += f"   📝 {status.description}\n"

    output += f"   📊 Index: {status.index}"

    if status.default:
        output += " ⭐ (Default)"

    if status.archived:
        output += " 📦 (Archived)"

    if status.color:
        output += f" 🎨 {status.color}"

    output += f"\n   🏗️ Project: {status.project.id}\n"

    return output


def format_status_list(
    status_list: StatusList,
    project_key: str | None = None,
    status_type: str | None = None,
) -> str:
    """Format a list of statuses for display.

    Args:
        status_list: StatusList schema instance
        project_key: Optional project key for context
        status_type: Optional status type for context

    Returns:
        Formatted status list string
    """
    if not status_list.values:
        filters = []
        if project_key:
            filters.append(f"project {project_key}")
        if status_type:
            filters.append(f"type {status_type}")
        filter_msg = f" for {' and '.join(filters)}" if filters else ""
        return f"📋 No statuses found{filter_msg}."

    # Create header with pagination info
    header = f"📋 **Found {len(status_list.values)} statuses"
    if status_list.total and status_list.total > len(status_list.values):
        start_num = status_list.startAt + 1
        end_num = status_list.startAt + len(status_list.values)
        header += f" (showing {start_num}-{end_num} of {status_list.total})"
    header += ":**\n\n"

    # Add filter context if provided
    if project_key or status_type:
        filters = []
        if project_key:
            filters.append(f"🏗️ Project: {project_key}")
        if status_type:
            filters.append(f"🏷️ Type: {status_type}")
        header += f"*Filters: {' | '.join(filters)}*\n\n"

    # Format each status
    formatted_statuses = []
    for status in status_list.values:
        formatted_statuses.append(format_status_display(status))

    return header + "\n".join(formatted_statuses)


def format_status_details(status: Status) -> str:
    """Format detailed status information for display.

    Args:
        status: Status schema instance

    Returns:
        Formatted status details string
    """
    output = f"🎯 **Status Details: {status.name}**\n\n"
    output += f"📊 **ID:** {status.id}\n"
    output += f"📝 **Name:** {status.name}\n"

    if status.description:
        output += f"📋 **Description:** {status.description}\n"

    output += f"📈 **Index:** {status.index}\n"
    output += f"⭐ **Default:** {'Yes' if status.default else 'No'}\n"
    output += f"📦 **Archived:** {'Yes' if status.archived else 'No'}\n"

    if status.color:
        output += f"🎨 **Color:** {status.color}\n"

    output += f"🏗️ **Project ID:** {status.project.id}\n"

    return output.strip()


def format_folder_display(folder: Folder) -> str:
    """Format a single folder for display.

    Args:
        folder: Folder schema instance

    Returns:
        Formatted folder string
    """
    output = f"**{folder.name}** (ID: {folder.id})\n"
    output += f"   📁 Type: {folder.folder_type.value}\n"
    output += f"   📊 Index: {folder.index}\n"

    if folder.parent_id:
        output += f"   📂 Parent ID: {folder.parent_id}\n"
    else:
        output += "   📂 Root folder\n"

    if folder.project:
        output += f"   🏗️ Project: {folder.project.id}\n"

    return output


def format_folder_list(
    folder_list: FolderList,
    project_key: str | None = None,
    folder_type: str | None = None,
) -> str:
    """Format a list of folders for display.

    Args:
        folder_list: FolderList schema instance
        project_key: Optional project key for context
        folder_type: Optional folder type for context

    Returns:
        Formatted folder list string
    """
    if not folder_list.values:
        filters = []
        if project_key:
            filters.append(f"project {project_key}")
        if folder_type:
            filters.append(f"type {folder_type}")
        filter_msg = f" for {' and '.join(filters)}" if filters else ""
        return f"📁 No folders found{filter_msg}."

    # Create header with pagination info
    header = f"📁 **Found {len(folder_list.values)} folders"
    if folder_list.total and folder_list.total > len(folder_list.values):
        start_num = folder_list.startAt + 1
        end_num = folder_list.startAt + len(folder_list.values)
        header += f" (showing {start_num}-{end_num} of {folder_list.total})"
    header += ":**\n\n"

    # Add filter context if provided
    if project_key or folder_type:
        filters = []
        if project_key:
            filters.append(f"🏗️ Project: {project_key}")
        if folder_type:
            filters.append(f"📁 Type: {folder_type}")
        header += f"*Filters: {' | '.join(filters)}*\n\n"

    # Format each folder
    formatted_folders = []
    for folder in folder_list.values:
        formatted_folders.append(format_folder_display(folder))

    return header + "\n".join(formatted_folders)


def format_folder_details(folder: Folder) -> str:
    """Format detailed folder information for display.

    Args:
        folder: Folder schema instance

    Returns:
        Formatted folder details string
    """
    output = f"📁 **Folder Details: {folder.name}**\n\n"
    output += f"📊 **ID:** {folder.id}\n"
    output += f"📝 **Name:** {folder.name}\n"
    output += f"📁 **Type:** {folder.folder_type.value}\n"
    output += f"📈 **Index:** {folder.index}\n"

    if folder.parent_id:
        output += f"📂 **Parent ID:** {folder.parent_id}\n"
    else:
        output += "📂 **Parent:** Root folder\n"

    if folder.project:
        output += f"🏗️ **Project ID:** {folder.project.id}\n"

    return output.strip()


def format_test_step_display(step: TestStep, step_number: int) -> str:
    """Format a single test step with complete information."""

    if step.inline:
        output = f"**Step {step_number}:** 📝 Inline Step\n"
        output += f"📄 **Description:** {step.inline.description}\n"

        if step.inline.test_data:
            output += f"📊 **Test Data:** {step.inline.test_data}\n"

        if step.inline.expected_result:
            output += f"✅ **Expected Result:** {step.inline.expected_result}\n"

        return output.rstrip()

    elif step.test_case:
        output = f"**Step {step_number}:** 🔗 Test Case Delegation\n"
        output += f"🔗 **Test Case Key:** {step.test_case.test_case_key}\n"

        if step.test_case.parameters:
            output += "⚙️ **Parameters:**\n"
            for param in step.test_case.parameters:
                output += f"  • {param.name} ({param.type}): {param.value}\n"

        return output.rstrip()
    else:
        return f"**Step {step_number}:** ❓ Unknown step type"


def format_test_steps_list(
    test_steps_list: TestStepsList,
    test_case_key: str,
    max_results: int | None = None,
    start_at: int | None = None,
) -> str:
    """Format a list of test steps for display."""

    if not test_steps_list.values:
        return f"📝 No test steps found for test case {test_case_key}."

    # Create header with pagination info
    total_steps = len(test_steps_list.values)
    header = f"📝 **Found {total_steps} test steps for {test_case_key}"

    if test_steps_list.total and test_steps_list.total > len(test_steps_list.values):
        header += f" (showing {len(test_steps_list.values)} of {test_steps_list.total})"

    header += "**\n\n"

    # Format each test step
    steps_output = []
    start_index = start_at or 0
    for i, step in enumerate(test_steps_list.values):
        step_number = start_index + i + 1
        steps_output.append(format_test_step_display(step, step_number))

    # Add pagination info if applicable
    footer = ""
    if test_steps_list.total and test_steps_list.total > len(test_steps_list.values):
        start_num = (start_at or 0) + 1
        end_num = (start_at or 0) + len(test_steps_list.values)
        footer = (
            f"\n\n📄 **Pagination:** Showing results "
            f"{start_num}-{end_num} of {test_steps_list.total}"
        )

    return header + "\n\n".join(steps_output) + footer


def format_test_step_details(step: TestStep, step_number: int | None = None) -> str:
    """Format detailed view of a single test step."""

    step_header = f"**Step {step_number}**" if step_number else "**Test Step**"
    output = f"📝 {step_header}\n\n"

    if step.inline:
        output += "📋 **Type:** Inline Step\n"
        output += f"📄 **Description:** {step.inline.description}\n"

        if step.inline.test_data:
            output += f"📊 **Test Data:** {step.inline.test_data}\n"

        if step.inline.expected_result:
            output += f"✅ **Expected Result:** {step.inline.expected_result}\n"

        if step.inline.reflect_ref:
            output += f"🤖 **AI Reference:** {step.inline.reflect_ref}\n"

    elif step.test_case:
        output += "📋 **Type:** Test Case Delegation\n"
        output += f"🔗 **Test Case Key:** {step.test_case.test_case_key}\n"

        if step.test_case.parameters:
            output += "⚙️ **Parameters:**\n"
            for param in step.test_case.parameters:
                output += f"  • {param.name} ({param.type}): {param.value}\n"
    else:
        output += "❓ **Type:** Unknown step type\n"

    return output.strip()


def format_test_script_display(test_script: TestScript) -> str:
    """Format a test script for display."""

    output = f"📝 **Test Script (ID: {test_script.id})**\n"

    # Add script type with emoji
    type_emoji = "📄" if test_script.type == "plain" else "🔧"
    output += f"{type_emoji} **Type:** {test_script.type.upper()}\n\n"

    # Add script content with proper formatting
    output += f"📋 **Content:**\n```\n{test_script.text}\n```"

    return output


def format_test_script_details(test_script: TestScript) -> str:
    """Format detailed view of a test script."""

    output = "📝 **Test Script Details**\n\n"
    output += f"🆔 **Script ID:** {test_script.id}\n"

    # Format type with description
    if test_script.type == "plain":
        output += "📄 **Type:** Plain Text\n"
        output += "💡 **Description:** Traditional test script format\n"
    elif test_script.type == "bdd":
        output += "🔧 **Type:** BDD (Behavior-Driven Development)\n"
        output += "💡 **Description:** Supports remote execution via API plugin\n"

    output += "\n📋 **Script Content:**\n"
    output += f"```\n{test_script.text}\n```\n"

    # Add usage notes
    if test_script.type == "plain":
        output += (
            "\n💡 **Note:** You can convert this to step-by-step format "
            "using the test steps endpoint."
        )
    elif test_script.type == "bdd":
        output += (
            "\n💡 **Note:** This BDD script can be executed remotely "
            "via build system integration."
        )

    return output
