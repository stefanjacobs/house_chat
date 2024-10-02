from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, CallbackContext
# from openai import OpenAI, Audio
import openai
import logging
import os, io


# Logging-Konfiguration für Debugging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


# Telegram-Bot Token setzen
telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")

# OpenAI Client und API Key setzen
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def transcribe_audio(audio_file_data):
    """Transkribiert eine Audiodatei mit OpenAI Whisper auf Deutsch."""

    audio_file = io.BytesIO(audio_file_data)
    audio_file.name = "audio.ogg"
    audio_file.seek(0)
    transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file, language="de")
    return transcript.text


def generate_chat_response(messages):
    """Generiert eine Antwort auf eine Textnachricht mit dem OpenAI Modell."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    return response.choices[0].message.content


async def handle_audio(update: Update, context: CallbackContext):
    """Verarbeitet empfangene Audionachrichten von Telegram."""
    # Herunterladen der Audiodatei
    audio_file = await update.message.voice.get_file()
    
    # Datei als Bytearray herunterladen
    audio_file_data = await audio_file.download_as_bytearray()

    # Transkription auf Deutsch
    text = transcribe_audio(audio_file_data)

    # Senden des transkribierten Textes an den Nutzer
    await update.message.reply_text(f"Transkribierter Text: {text}")

    # Nachrichtenverlauf für ChatCompletion vorbereiten
    chat_history = [
        {"role": "system", "content": "Du bist ein hilfreicher Assistent."},
        {"role": "user", "content": text}
    ]

    # Antwort von OpenAI generieren
    ai_response = generate_chat_response(chat_history)

    # Senden der AI-Antwort an den Benutzer
    await update.message.reply_text(ai_response)


async def handle_text(update: Update, context: CallbackContext):
    """Verarbeitet empfangene Textnachrichten von Telegram."""
    # Textnachricht des Benutzers
    user_message = update.message.text

    # Nachrichtenverlauf für ChatCompletion vorbereiten
    chat_history = [
        {"role": "system", "content": "Du bist ein hilfreicher Assistent."},
        {"role": "user", "content": user_message}
    ]

    # Antwort von OpenAI generieren
    ai_response = generate_chat_response(chat_history)

    # Senden der AI-Antwort an den Benutzer
    await update.message.reply_text(ai_response)


async def start(update: Update, context: CallbackContext):
    """Begrüßt den Benutzer mit einer Nachricht."""
    await update.message.reply_text('Hallo! Ich bin dein Haus-Bot.')


def main():
    # Erstellen des Telegram-Bots mit dem Application-Builder
    application = Application.builder().token(telegram_token).build()

    # Hinzufügen der Audio- und Text-Handler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VOICE, handle_audio))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Starten des Bots
    application.run_polling()


if __name__ == '__main__':
    main()
