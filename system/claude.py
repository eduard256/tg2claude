"""Claude Code interaction module."""

import asyncio
import os
import subprocess
from typing import AsyncGenerator, Optional
from config import WORKSPACE_DIR, CLAUDE_BASE_CMD


async def run_claude(user_id: int, prompt: str, session_id: Optional[str] = None) -> AsyncGenerator[str, None]:
    """
    Run Claude Code subprocess and yield output lines.

    Args:
        user_id: Telegram user ID
        prompt: User message
        session_id: Optional Claude session ID for resuming

    Yields:
        Lines from Claude Code stdout
    """
    # Build command
    cmd = CLAUDE_BASE_CMD.copy()

    if session_id:
        # Resume existing session
        cmd.extend(["--resume", session_id])

    # Add prompt
    cmd.extend(["-p", prompt])

    # Start subprocess in workspace directory
    # Set limit to 10MB to handle large JSON lines from Claude Code
    # Pass environment variables to ensure Claude Code can find MCP config
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=WORKSPACE_DIR,
        env=os.environ.copy(),  # Pass current environment including HOME
        limit=10 * 1024 * 1024  # 10 MB buffer for large tool results
    )

    # Read stdout line by line
    while True:
        line = await process.stdout.readline()
        if not line:
            break

        # Decode and yield line
        yield line.decode("utf-8", errors="ignore").rstrip()

    # Wait for process to complete
    await process.wait()


def kill_process(process: asyncio.subprocess.Process) -> None:
    """Kill a subprocess if it exists and is running."""
    if process and process.returncode is None:
        try:
            process.terminate()
        except:
            pass