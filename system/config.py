"""Configuration module for tg2claude bot."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent.parent  # tg2claude/
WORKSPACE_DIR = BASE_DIR / "workspace"
SESSIONS_DIR = BASE_DIR / "sessions"
PROMPT_FILE = BASE_DIR / "system" / "PROMPT.md"

# Telegram configuration
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "")

# Parse allowed users as set of integers
allowed_users_str = os.getenv("ALLOWED_USERS", "")
ALLOWED_USERS = {int(uid.strip()) for uid in allowed_users_str.split(",") if uid.strip()}

# Claude command configuration
CLAUDE_MODEL = "sonnet"
CLAUDE_BASE_CMD = [
    "claude",
    "--dangerously-skip-permissions",
    "--verbose",
    "--model", CLAUDE_MODEL,
    "--output-format", "stream-json",
    "--system-prompt-file", "../system/PROMPT.md"
]