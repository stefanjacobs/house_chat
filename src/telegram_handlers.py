
from telegram import Update
from telegram.ext import CallbackContext
from src.telegram_user_id_manager import user_id_manager
from src.tools.todo_app import todo_app

from src.ai_responses import generate_chat_response, transcribe_audio
import src.ai_chat_history as ai_chat_history

import logging

async def handle_audio(update: Update, context: CallbackContext):
    """Verarbeitet empfangene Audionachrichten von Telegram."""
    # Herunterladen der Audiodatei als Bytearray
    audio_file = await update.message.voice.get_file()
    audio_file_data = await audio_file.download_as_bytearray()

    # Transkription auf Deutsch und Senden des transkribierten Textes an den Nutzer
    text = await transcribe_audio(audio_file_data)
    await update.message.reply_text(f"Transkribierter Text: {text}")

    ai_response = await generate_chat_response(text)

    await update.message.reply_text(ai_response)


async def handle_text(update: Update, context: CallbackContext):
    """Verarbeitet empfangene Textnachrichten von Telegram."""
    # Textnachricht des Benutzers
    user_message = update.message.text

    # Antwort von OpenAI generieren
    ai_response = await generate_chat_response(user_message)

    await update.message.reply_text(ai_response)


async def start(update: Update, context: CallbackContext):
    """Begrüßt den Benutzer mit einer Nachricht."""
    global user_id_manager
    user_id = update.message.chat_id
    await user_id_manager.add_user(user_id)
    await update.message.reply_text('Hallo! Ich bin dein Hauself Dobbi.')


async def reset(update: Update, context: CallbackContext):
    """Setzt den Chatverlauf zurück."""
    ai_chat_history.CHAT_HISTORY = ai_chat_history.reset_history()
    await update.message.reply_text('Chatverlauf zurückgesetzt.')


async def error_handler(update: Update, context: CallbackContext):
    """Loggt Fehler und informiert den Benutzer."""
    logging.error(msg="Exception während eines Updates:", exc_info=context.error)

    await update.message.reply_text('Es ist ein unerwarteter Fehler aufgetreten. Bitte versuchen Sie es später erneut.')


async def post_init(_application):
    """Initialisierung des Bots."""
    await user_id_manager.connect()
    await todo_app.connect()


async def post_shutdown(_application):
    """Herunterfahren des Bots."""
    await user_id_manager.shutdown()
    await todo_app.shutdown()
