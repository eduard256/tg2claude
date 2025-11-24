"""JSON parser module for Claude Code stream output."""

import json
from typing import Dict, Any, Optional


def parse_line(line: str) -> Optional[Dict[str, Any]]:
    """
    Parse single JSON line from Claude Code output.
    Returns dict with type and data for Telegram.
    """
    if not line.strip():
        return None

    try:
        data = json.loads(line)
        return data
    except json.JSONDecodeError:
        return None


def format_tool_use(tool_use: Dict[str, Any]) -> str:
    """
    Format tool_use object for Telegram.
    Returns formatted string with name and truncated input.
    """
    name = tool_use.get("name", "Unknown")
    input_data = tool_use.get("input", {})

    # Convert input to JSON string and truncate
    try:
        input_str = json.dumps(input_data, ensure_ascii=False, indent=2)
        if len(input_str) > 300:
            input_str = input_str[:297] + "..."
    except:
        input_str = str(input_data)[:300]

    return f"🔧 {name}\n```json\n{input_str}\n```"


def format_tool_result(result: Dict[str, Any]) -> str:
    """
    Format tool result for Telegram.
    Returns formatted string with first 5 lines.
    """
    # Extract result content
    content = ""

    if isinstance(result, dict):
        # Try to extract content from different possible structures
        if "content" in result:
            content = str(result["content"])
        elif "output" in result:
            content = str(result["output"])
        else:
            content = json.dumps(result, ensure_ascii=False, indent=2)
    else:
        content = str(result)

    # Split into lines and take first 5
    lines = content.split("\n")
    if len(lines) > 5:
        preview = "\n".join(lines[:5])
        return f"📥 Результат:\n```\n{preview}\n...\n```"
    else:
        return f"📥 Результат:\n```\n{content}\n```"


def extract_message_content(data: Dict[str, Any]) -> Optional[str]:
    """
    Extract message content from Claude response.
    Returns formatted text for Telegram or None.
    """
    msg_type = data.get("type")

    if msg_type == "system":
        # Extract session_id from system messages (but don't show to user)
        return None

    elif msg_type == "assistant":
        message = data.get("message", {})
        content = message.get("content", [])

        if not content:
            return None

        # Process content array
        result_parts = []
        for item in content:
            if isinstance(item, dict):
                content_type = item.get("type")

                if content_type == "text":
                    text = item.get("text", "")
                    if text:
                        result_parts.append(text)

                elif content_type == "tool_use":
                    formatted = format_tool_use(item)
                    result_parts.append(formatted)

        return "\n\n".join(result_parts) if result_parts else None

    elif msg_type == "user":
        # Handle tool results
        tool_results = data.get("tool_use_result", [])
        if tool_results:
            result_parts = []
            for result in tool_results:
                if isinstance(result, dict) and "content" in result:
                    formatted = format_tool_result(result)
                    result_parts.append(formatted)
            return "\n\n".join(result_parts) if result_parts else None

    elif msg_type == "result":
        # Final result message
        if data.get("subtype") == "success":
            return "✅ Завершено"
        elif data.get("is_error"):
            error = data.get("error", "Unknown error")
            return f"❌ Ошибка: {error}"

    return None