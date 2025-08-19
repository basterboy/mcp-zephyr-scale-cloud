"""Formatting utilities for MCP tool outputs."""

from typing import Any

from ..schemas.priority import Priority, PriorityList


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
