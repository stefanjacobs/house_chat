
import os
from telegram import Bot
from telegramify_markdown import markdownify
from src.telegram_user_id_manager import user_id_manager
from logging import getLogger
import asyncio

async def broadcast_message(message_text):
    bot = Bot(os.getenv("TELEGRAM_BOT_TOKEN"))
    global user_id_manager
    user_ids = user_id_manager.get_all_users()
    for user_id in user_ids:
        try:
            await bot.send_message(chat_id=user_id, text=markdownify(message_text), parse_mode="MarkdownV2")
            await asyncio.sleep(1)  # Um Telegram-Ratenbegrenzungen zu vermeiden
        except Exception as e:
            pass
            # logger.error(f"Fehler beim Senden an {user_id}: {e}")