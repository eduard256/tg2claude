"""Session management module for tg2claude bot."""

import json
from pathlib import Path
from typing import Dict, Any
from config import SESSIONS_DIR


def get_session_file(user_id: int) -> Path:
    """Get session file path for user."""
    return SESSIONS_DIR / f"{user_id}.json"


def get_session(user_id: int) -> Dict[str, Any]:
    """
    Get session data for user.
    Returns dict with claude_session_id and locked.
    If file doesn't exist, returns empty dict with locked=False.
    """
    session_file = get_session_file(user_id)

    if not session_file.exists():
        return {"locked": False}

    try:
        with open(session_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure locked field exists
            if "locked" not in data:
                data["locked"] = False
            return data
    except (json.JSONDecodeError, IOError):
        return {"locked": False}


def save_session(user_id: int, data: Dict[str, Any]) -> None:
    """Save session data for user."""
    session_file = get_session_file(user_id)

    # Ensure sessions directory exists
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    with open(session_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def delete_session(user_id: int) -> None:
    """Delete session file for user."""
    session_file = get_session_file(user_id)

    if session_file.exists():
        session_file.unlink()