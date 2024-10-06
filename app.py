from dotenv import load_dotenv
load_dotenv(".envrc")


import os, logging

from telegram.ext import Application, CommandHandler, MessageHandler, filters

from src.telegram_handlers import handle_audio, handle_text, start, reset


# Logging-Konfiguration für Debugging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


def main():
    # Erstellen des Telegram-Bots mit dem Application-Builder
    application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    # Hinzufügen der Audio- und Text-Handler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reset", reset))
    application.add_handler(MessageHandler(filters.VOICE, handle_audio))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
    )

    # Starten des Bots
    application.run_polling()


if __name__ == "__main__":
    main()
