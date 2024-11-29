
from telegram import Update
from telegram.ext import CallbackContext
from telegramify_markdown import markdownify
from src.telegram_user_data import USER_DATA, create_user_data, reset_history
from src.telegram_user_id_manager import user_id_manager

from src.ai_responses import generate_chat_response, transcribe_audio
from src.scheduler import my_scheduler

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
    # await update.message.reply_text(markdownify(f"Transkribierter Text: {text}"), parse_mode="MarkdownV2")

    ai_response = await generate_chat_response(text, USER_DATA[user_id])
    await update.message.reply_text(markdownify(ai_response), parse_mode="MarkdownV2")


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
    await update.message.reply_text(markdownify(ai_response), parse_mode="MarkdownV2")


async def start(update: Update, context: CallbackContext):
    """Begrüßt den Benutzer mit einer Nachricht."""
    global user_id_manager
    global USER_DATA

    user_id = update.message.chat_id
    await create_user_data(user_id)
    await user_id_manager.add_user(user_id)
    await update.message.reply_text(markdownify('Hallo! Ich bin dein Hauself Dobbi.'), parse_mode="MarkdownV2")


async def reset(update: Update, context: CallbackContext):
    """Setzt den Chatverlauf zurück."""
    global USER_DATA
    user_id = update.message.chat_id
    await reset_history(user_id)
    await update.message.reply_text(markdownify('...Obliviate... - Dobbi hat alles vergessen.'), parse_mode="MarkdownV2")


async def error_handler(update: Update, context: CallbackContext):
    """Loggt Fehler und informiert den Benutzer."""
    logging.error(msg="Exception während eines Updates:", exc_info=context.error)

    await update.message.reply_text(markdownify('Dobbi ist ein misslicher Fehler unterlaufen. Tut mir leid...'), parse_mode="MarkdownV2")


async def post_init(_application):
    """Initialisierung des Bots."""
    await user_id_manager.connect()
    scheduler = my_scheduler()
    scheduler.start()


async def post_shutdown(_application):
    """Herunterfahren des Bots."""
    await user_id_manager.shutdown()
