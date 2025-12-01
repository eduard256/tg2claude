#!/usr/bin/env python3
"""Test script to reproduce exact bot subprocess behavior."""

import asyncio
import os
import sys
from pathlib import Path

# Add system directory to path
sys.path.insert(0, str(Path(__file__).parent / "system"))

from config import WORKSPACE_DIR, CLAUDE_BASE_CMD


async def run_claude_test():
    """Run Claude exactly as the bot does."""
    # Build command exactly like bot
    cmd = CLAUDE_BASE_CMD.copy()
    cmd.extend(["-p", "у тебя есть mcp?"])

    print(f"Command: {' '.join(cmd)}")
    print(f"Working directory: {WORKSPACE_DIR}")
    print(f"HOME env var: {os.environ.get('HOME')}")
    print(f"\n{'='*60}\n")

    # Start subprocess EXACTLY as bot does
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=WORKSPACE_DIR,
        env=os.environ.copy(),
        limit=10 * 1024 * 1024
    )

    # Read stdout line by line exactly as bot does
    line_count = 0
    while True:
        line = await process.stdout.readline()
        if not line:
            break

        decoded = line.decode("utf-8", errors="ignore").rstrip()
        line_count += 1

        # Print first line (system init with tools list)
        if line_count == 1:
            print(f"LINE {line_count}:")
            print(decoded)
            print(f"\n{'='*60}\n")
        # Print assistant response
        elif '"type":"assistant"' in decoded:
            print(f"LINE {line_count}:")
            print(decoded)
            print(f"\n{'='*60}\n")

    await process.wait()
    print(f"\nTotal lines received: {line_count}")
    print(f"Exit code: {process.returncode}")


if __name__ == "__main__":
    asyncio.run(run_claude_test())
