import os, logging, datetime, pytz

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from telegram import Bot

from src.telegram_user_data import USER_DATA, create_user_data
from src.telegram_user_id_manager import user_id_manager
from src.ai_responses import generate_chat_response


# TODO: User-Data ist das falsche Objekt. Das ist nicht initialisiert. Besser wäre eine Funktion, die Jobs anlegt per Funktion und hier wird dann pro User der Job ausgeführt nach dem u.g. Schema - aber für einen ersten Wurf ist das nice!

async def weather_job():
    # report weather
    bot = Bot(os.getenv("TELEGRAM_BOT_TOKEN"))
    global USER_DATA, user_id_manager
    all_users = await user_id_manager.get_all_users()
    for user_id in all_users:
        if user_id in USER_DATA:
            continue
        await create_user_data(user_id)

    current_date = datetime.datetime.now(tz=pytz.timezone("Europe/Berlin")).strftime("%Y-%m-%d %H:%M")
    for user_id in USER_DATA.keys():
        ai_response = await generate_chat_response(f"Datum und Uhrzeit: {current_date}. Wie wird das Wetter heute?", USER_DATA[user_id])
        try:
            await bot.send_message(chat_id=user_id, text=ai_response)
        except Exception as e:
            logging.error(f"Fehler beim Senden an {user_id}: {e}")


async def weather_forecast_job():
    # report weather
    bot = Bot(os.getenv("TELEGRAM_BOT_TOKEN"))
    global USER_DATA, user_id_manager
    all_users = await user_id_manager.get_all_users()
    for user_id in all_users:
        if user_id in USER_DATA:
            continue
        await create_user_data(user_id)

    current_date = datetime.datetime.now(tz=pytz.timezone("Europe/Berlin")).strftime("%Y-%m-%d %H:%M")
    for user_id in USER_DATA.keys():
        ai_response = await generate_chat_response(f"Datum und Uhrzeit jetzt: {current_date}. Wie wird das Wetter in den kommenden Tagen?", USER_DATA[user_id])
        try:
            await bot.send_message(chat_id=user_id, text=ai_response)
        except Exception as e:
            logging.error(f"Fehler beim Senden an {user_id}: {e}")


async def energy_prices_job():
    # report energy prices
    bot = Bot(os.getenv("TELEGRAM_BOT_TOKEN"))
    global USER_DATA, user_id_manager
    all_users = await user_id_manager.get_all_users()
    for user_id in all_users:
        if user_id in USER_DATA:
            continue
        await create_user_data(user_id)

    current_date = datetime.datetime.now(tz=pytz.timezone("Europe/Berlin")).strftime("%Y-%m-%d %H:%M")
    for user_id in USER_DATA.keys():
        ai_response = await generate_chat_response(f"Aktuelles Datum und jetzige Uhrzeit: {current_date}. Wie entwickeln sich die Energiepreise bis morgen Abend, 24 Uhr? Wann ist der Strom besonders günstig?", USER_DATA[user_id])
        try:
            await bot.send_message(chat_id=user_id, text=ai_response)
        except Exception as e:
            logging.error(f"Fehler beim Senden an {user_id}: {e}")


# async def test_job():
#     print("Test-Job fired!")


def my_scheduler():
    scheduler = AsyncIOScheduler()

    morning_cron = CronTrigger(hour=7, minute=0)
    scheduler.add_job(weather_job, morning_cron)

    noon_cron = CronTrigger(hour=12, minute=0)
    scheduler.add_job(weather_forecast_job, morning_cron)

    lunch_cron = CronTrigger(hour=14, minute=0)
    scheduler.add_job(energy_prices_job, lunch_cron)

    # test_cron = CronTrigger(minute="*/1")
    # scheduler.add_job(test_job, test_cron)

    return scheduler
