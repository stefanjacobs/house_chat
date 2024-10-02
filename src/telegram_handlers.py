
from telegram import Update
from telegram.ext import CallbackContext

from src.ai_responses import generate_chat_response, transcribe_audio
import src.ai_chat_history as ai_chat_history


async def handle_audio(update: Update, context: CallbackContext):
    """Verarbeitet empfangene Audionachrichten von Telegram."""
    # Herunterladen der Audiodatei als Bytearray
    audio_file = await update.message.voice.get_file()
    audio_file_data = await audio_file.download_as_bytearray()

    # Transkription auf Deutsch und Senden des transkribierten Textes an den Nutzer
    text = transcribe_audio(audio_file_data)
    await update.message.reply_text(f"Transkribierter Text: {text}")

    # Antwort von OpenAI generieren und an die History anhängen
    ai_response = generate_chat_response(text)

    await update.message.reply_text(ai_response)


async def handle_text(update: Update, context: CallbackContext):
    """Verarbeitet empfangene Textnachrichten von Telegram."""
    # Textnachricht des Benutzers
    user_message = update.message.text

    # Antwort von OpenAI generieren
    ai_response = generate_chat_response(user_message)

    await update.message.reply_text(ai_response)


async def start(update: Update, context: CallbackContext):
    """Begrüßt den Benutzer mit einer Nachricht."""
    await update.message.reply_text('Hallo! Ich bin dein Haus-Bot.')


async def reset(update: Update, context: CallbackContext):
    """Setzt den Chatverlauf zurück."""
    ai_chat_history.CHAT_HISTORY = ai_chat_history.reset_history()
    await update.message.reply_text('Chatverlauf zurückgesetzt.')