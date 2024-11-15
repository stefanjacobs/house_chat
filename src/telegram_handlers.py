
from telegram import Update
from telegram.ext import CallbackContext
from src.telegram_user_data import USER_DATA, create_user_data, reset_history
from src.telegram_user_id_manager import user_id_manager
# from src.tools.todo_app import get_overdue_todos, create_todo, get_categories, get_todos_by_category, update_todo, get_open_todos

from src.ai_responses import generate_chat_response, transcribe_audio

import logging

async def handle_audio(update: Update, context: CallbackContext):
    """Verarbeitet empfangene Audionachrichten von Telegram."""
    global USER_DATA

    # Herunterladen der Audiodatei als Bytearray
    user_id = update.message.chat_id
    if not user_id in USER_DATA:
        await create_user_data(user_id)
    audio_file = await update.message.voice.get_file()
    audio_file_data = await audio_file.download_as_bytearray()

    # Transkription auf Deutsch und Senden des transkribierten Textes an den Nutzer
    text = await transcribe_audio(audio_file_data)
    # await update.message.reply_text(f"Transkribierter Text: {text}")

    ai_response = await generate_chat_response(text, USER_DATA[user_id])
    await update.message.reply_text(ai_response)


async def handle_text(update: Update, context: CallbackContext):
    """Verarbeitet empfangene Textnachrichten von Telegram."""
    global USER_DATA

    # Textnachricht des Benutzers
    user_message = update.message.text
    user_id = update.message.chat_id
    if not user_id in USER_DATA:
        await create_user_data(user_id)

    # Antwort von OpenAI generieren
    ai_response = await generate_chat_response(user_message, USER_DATA[user_id])
    await update.message.reply_text(ai_response)


async def start(update: Update, context: CallbackContext):
    """Begrüßt den Benutzer mit einer Nachricht."""
    global user_id_manager
    global USER_DATA

    user_id = update.message.chat_id
    await create_user_data(user_id)
    await user_id_manager.add_user(user_id)
    await update.message.reply_text('Hallo! Ich bin dein Hauself Dobbi.')


async def reset(update: Update, context: CallbackContext):
    """Setzt den Chatverlauf zurück."""
    global USER_DATA
    user_id = update.message.chat_id
    await reset_history(user_id)
    await update.message.reply_text('...Obliviate... - Dobbi hat alles vergessen.')


async def error_handler(update: Update, context: CallbackContext):
    """Loggt Fehler und informiert den Benutzer."""
    logging.error(msg="Exception während eines Updates:", exc_info=context.error)

    await update.message.reply_text('Dobbi ist ein misslicher Fehler unterlaufen. Tut mir leid...')


async def post_init(_application):
    """Initialisierung des Bots."""
    await user_id_manager.connect()


async def post_shutdown(_application):
    """Herunterfahren des Bots."""
    await user_id_manager.shutdown()
