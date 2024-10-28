from dotenv import load_dotenv
load_dotenv(".envrc")


import os, logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from src.telegram_handlers import handle_audio, handle_text, start, reset, error_handler, post_init, post_shutdown

from src.scheduler import my_scheduler

# Logging-Konfiguration für Debugging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


def main():

    # Initialisierung des Schedulers
    scheduler = my_scheduler()
    scheduler.start()

    # Erstellen des Telegram-Bots mit dem Application-Builder
    application = (Application.builder()
                .token(os.getenv("TELEGRAM_BOT_TOKEN"))
                .post_init(post_init)
                .post_shutdown(post_shutdown)
                .build())

    # Hinzufügen der Audio- und Text-Handler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reset", reset))
    application.add_handler(MessageHandler(filters.VOICE, handle_audio))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
    )
    application.add_error_handler(error_handler)

    # Starten des Bots
    application.run_polling()

    # Shutdown des Schedulers wenn der Bot heruntergefahren wird
    # scheduler.shutdown()



if __name__ == "__main__":
    main()
