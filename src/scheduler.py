import os, logging, datetime, pytz

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from telegram import Bot

from src.telegram_user_data import USER_DATA
from src.ai_responses import generate_chat_response


# TODO: User-Data ist das falsche Objekt. Das ist nicht initialisiert. Besser wäer eine Funktion, die Jobs anlegt per Funktion und hier wird dann pro User der Job ausgeführt nach dem u.g. Schema - aber für einen ersten Wurf ist das nice!

async def weather_job():
    # report weather
    bot = Bot(os.getenv("TELEGRAM_BOT_TOKEN"))
    global USER_DATA
    current_date = datetime.datetime.now(tz=pytz.timezone("Europe/Berlin")).strftime("%Y-%m-%d %H:%M")
    for user_id in USER_DATA.keys():
        ai_response = await generate_chat_response(f"Datum und Uhrzeit: {current_date}. Wie wird das Wetter heute?", USER_DATA[user_id])
        try:
            await bot.send_message(chat_id=user_id, text=ai_response)
        except Exception as e:
            logging.error(f"Fehler beim Senden an {user_id}: {e}")


async def energy_prices_job():
    # report energy prices
    bot = Bot(os.getenv("TELEGRAM_BOT_TOKEN"))
    global USER_DATA
    current_date = datetime.datetime.now(tz=pytz.timezone("Europe/Berlin")).strftime("%Y-%m-%d %H:%M")
    for user_id in USER_DATA.keys():
        ai_response = await generate_chat_response(f"Datum und Uhrzeit: {current_date}. Wie entwickeln sich die Energiepreise bis morgen Nacht? Wann ist der Strom besonders günstig?", USER_DATA[user_id])
        try:
            await bot.send_message(chat_id=user_id, text=ai_response)
        except Exception as e:
            logging.error(f"Fehler beim Senden an {user_id}: {e}")


def my_scheduler():
    scheduler = AsyncIOScheduler()

    morning_cron = CronTrigger(hour=23, minute=3)
    scheduler.add_job(weather_job, morning_cron)

    lunch_cron = CronTrigger(hour=14, minute=0)
    scheduler.add_job(energy_prices_job, lunch_cron)

    return scheduler
