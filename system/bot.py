"""Main bot module for tg2claude."""

import asyncio
import logging
from typing import Dict, Optional

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode

from config import TG_BOT_TOKEN, ALLOWED_USERS
from sessions import get_session, save_session, delete_session
from parser import parse_line, extract_message_content
from claude import run_claude

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=TG_BOT_TOKEN)
dp = Dispatcher()

# Active processes by user_id
processes: Dict[int, asyncio.Task] = {}


def format_user_prompt(message: types.Message) -> str:
    """Format user message with metadata for Claude."""
    user = message.from_user

    user_info = f"""Информация о пользователе:
- ID: {user.id}
- Username: @{user.username if user.username else 'none'}
- Имя: {user.full_name}
- Язык: {user.language_code if user.language_code else 'unknown'}

Сообщение:
{message.text}"""

    return user_info


async def process_claude_stream(user_id: int, chat_id: int, prompt: str):
    """Process Claude Code stream and send messages to Telegram."""
    session = get_session(user_id)
    session_id = session.get("claude_session_id")

    # Lock session
    session["locked"] = True
    save_session(user_id, session)

    current_session_id = None
    message_buffer = []
    last_message = None

    try:
        async for line in run_claude(user_id, prompt, session_id):
            if not line:
                continue

            data = parse_line(line)
            if not data:
                continue

            # Extract session_id from system messages
            if data.get("type") == "system" and data.get("subtype") == "init":
                current_session_id = data.get("session_id")
                if current_session_id:
                    session["claude_session_id"] = current_session_id
                    save_session(user_id, session)

            # Extract and send content
            content = extract_message_content(data)
            if content:
                # Send message to Telegram
                try:
                    last_message = await bot.send_message(
                        chat_id,
                        content,
                        parse_mode=ParseMode.MARKDOWN
                    )
                except Exception as e:
                    # Try without markdown if it fails
                    try:
                        last_message = await bot.send_message(chat_id, content)
                    except:
                        logger.error(f"Failed to send message: {e}")

            # Check if result received (unlock session)
            if data.get("type") == "result":
                session["locked"] = False
                save_session(user_id, session)

    except Exception as e:
        logger.error(f"Error processing Claude stream: {e}")
        try:
            await bot.send_message(chat_id, f"❌ Ошибка: {str(e)}")
        except:
            pass
    finally:
        # Ensure session is unlocked
        session = get_session(user_id)
        session["locked"] = False
        save_session(user_id, session)

        # Remove from active processes
        if user_id in processes:
            del processes[user_id]


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Handle /start command - reset session."""
    user_id = message.from_user.id

    # Check if user is allowed
    if user_id not in ALLOWED_USERS:
        return

    # Kill active process if exists
    if user_id in processes:
        task = processes[user_id]
        if not task.done():
            task.cancel()
        del processes[user_id]

    # Delete session file
    delete_session(user_id)

    await message.reply("🔄 Сессия очищена. Можете начать новый диалог.")


@dp.message()
async def handle_message(message: types.Message):
    """Handle all text messages."""
    user_id = message.from_user.id

    # Check if user is allowed
    if user_id not in ALLOWED_USERS:
        return

    # Check if session is locked
    session = get_session(user_id)
    if session.get("locked", False):
        await message.reply("⏳ Дождитесь завершения предыдущего запроса.")
        return

    # Check if there's an active process (shouldn't happen with proper locking)
    if user_id in processes and not processes[user_id].done():
        await message.reply("⏳ Дождитесь завершения предыдущего запроса.")
        return

    # Format prompt
    prompt = format_user_prompt(message)

    # Start processing in background
    task = asyncio.create_task(
        process_claude_stream(user_id, message.chat.id, prompt)
    )
    processes[user_id] = task

    # Send initial message
    await message.reply("🤖 Обрабатываю запрос...")


async def main():
    """Main bot entry point."""
    logger.info("Starting tg2claude bot...")

    # Check configuration
    if not TG_BOT_TOKEN:
        logger.error("TG_BOT_TOKEN not set in .env file!")
        return

    if not ALLOWED_USERS:
        logger.warning("ALLOWED_USERS is empty - no users will be able to use the bot!")
    else:
        logger.info(f"Allowed users: {ALLOWED_USERS}")

    # Start polling
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        # Cancel all active tasks
        for task in processes.values():
            if not task.done():
                task.cancel()

        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())