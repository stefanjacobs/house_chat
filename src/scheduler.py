import os, logging, datetime, pytz

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from telegram import Bot
from telegramify_markdown import markdownify

from src.telegram_user_data import USER_DATA, create_user_data
from src.telegram_user_id_manager import user_id_manager
from src.ai_responses import generate_chat_response
from src.ai_prompts import get_schedule_sysprompt

import src.tools.trash_app as trash
import src.tools.dwd_app as dwd
import src.tools.todo_app as todo
import src.tools.news_app as news


async def init_scheduler_job():
    """
    We handle two issues here:
    - We make sure that all users have a USER_DATA object, because it may be the case that the user has not yet sent a message to the bot since restart
    - We create a schedule_user_data object that is only used in the context of the scheduler. This object is same as the USER_DATA object, but only contains the chat history and the user_id of the schedule run. Only the response of the scheduler is stored the global USER_DATA object.
    """
    bot = Bot(os.getenv("TELEGRAM_BOT_TOKEN"))
    global USER_DATA, user_id_manager
    all_users = await user_id_manager.get_all_users()
    for user_id in all_users:
        if user_id in USER_DATA:
            continue
        await create_user_data(user_id)
    
    current_date = datetime.datetime.now(tz=pytz.timezone("Europe/Berlin")).strftime("%Y-%m-%d %H:%M")
    schedule_user_data = dict()
    for user_id in USER_DATA.keys():
        schedule_user_data[user_id] = dict()
        schedule_user_data[user_id]["user_id"] = user_id
        schedule_user_data[user_id]["chat_history"] = [
            {"role": "system", "content": get_schedule_sysprompt(current_date)}
        ]
    return bot, schedule_user_data


# TODO: User-Data ist das falsche Objekt. Das ist nicht initialisiert. Besser wäre eine Funktion, die Jobs anlegt per Funktion und hier wird dann pro User der Job ausgeführt nach dem u.g. Schema - aber für einen ersten Wurf ist das nice!

async def weather_job():
    global USER_DATA
    bot, schedule_user_data = await init_scheduler_job()
    for user_id in schedule_user_data.keys():
        ai_response = await generate_chat_response(f"Wie wird das Wetter heute?", schedule_user_data[user_id])
        try:
            await bot.send_message(chat_id=user_id, text=markdownify(ai_response), parse_mode="MarkdownV2")
            USER_DATA[user_id]["chat_history"].append({"role": "assistant", "content": ai_response})
        except Exception as e:
            logging.error(f"Fehler beim Senden an {user_id}: {e}")


async def weather_forecast_job():
    global USER_DATA
    bot, schedule_user_data = await init_scheduler_job()
    for user_id in USER_DATA.keys():
        ai_response = await generate_chat_response(f"Wie wird das Wetter in den kommenden Tagen?", schedule_user_data[user_id])
        try:
            await bot.send_message(chat_id=user_id, text=markdownify(ai_response), parse_mode="MarkdownV2")
            USER_DATA[user_id]["chat_history"].append({"role": "assistant", "content": ai_response})
        except Exception as e:
            logging.error(f"Fehler beim Senden an {user_id}: {e}")


async def energy_prices_job():
    global USER_DATA
    bot, schedule_user_data = await init_scheduler_job()
    for user_id in USER_DATA.keys():
        ai_response = await generate_chat_response(f"Wie entwickeln sich die Energiepreise bis morgen Abend, 24 Uhr? Wann ist der Strom besonders günstig?", schedule_user_data[user_id])
        try:
            await bot.send_message(chat_id=user_id, text=markdownify(ai_response), parse_mode="MarkdownV2")
            USER_DATA[user_id]["chat_history"].append({"role": "assistant", "content": ai_response})
        except Exception as e:
            logging.error(f"Fehler beim Senden an {user_id}: {e}")


async def dwd_warning_job():
    # report weather warnings
    global USER_DATA
    bot, schedule_user_data = await init_scheduler_job()
    result, warn = dwd.check_new_warnings()
    if not result:
        return
    for user_id in USER_DATA.keys():
        ai_response = await generate_chat_response(f"Folgende Wetterwarnungen liegen vor: {warn}. Bitte informiere den Nutzer über die jetzt wichtigsten Warnungen.", schedule_user_data[user_id])
        try:
            await bot.send_message(chat_id=user_id, text=markdownify(ai_response), parse_mode="MarkdownV2")
            USER_DATA[user_id]["chat_history"].append({"role": "assistant", "content": ai_response})
        except Exception as e:
            logging.error(f"Fehler beim Senden an {user_id}: {e}")


async def tomorrow_trash_job():
    # report energy prices
    global USER_DATA
    bot, schedule_user_data = await init_scheduler_job()
    result = await trash.get_tomorrows_trash()
    if len(result) == 0:
        return
    if result == "" or result == "[]":
        return
    for user_id in USER_DATA.keys():
        ai_response = await generate_chat_response(f"Welcher Müll wird morgen abgeholt?", schedule_user_data[user_id])
        try:
            await bot.send_message(chat_id=user_id, text=markdownify(ai_response), parse_mode="MarkdownV2")
            USER_DATA[user_id]["chat_history"].append({"role": "assistant", "content": ai_response})
        except Exception as e:
            logging.error(f"Fehler beim Senden an {user_id}: {e}")


async def reminder_job():
    # report open and due todos
    global USER_DATA
    bot, schedule_user_data = await init_scheduler_job()
    
    result = await todo.get_overdue_todos()
    if result == "[]": # empty list, no overdue items
        return

    for user_id in USER_DATA.keys():
        ai_response = await generate_chat_response(f"Welche Todos sind überfällig?", schedule_user_data[user_id])
        try:
            await bot.send_message(chat_id=user_id, text=markdownify(ai_response), parse_mode="MarkdownV2")
            USER_DATA[user_id]["chat_history"].append({"role": "assistant", "content": ai_response})
        except Exception as e:
            logging.error(f"Fehler beim Senden an {user_id}: {e}")


async def news_job():
    global USER_DATA
    bot, schedule_user_data = await init_scheduler_job()
    
    for user_id in USER_DATA.keys():
        ai_response = await generate_chat_response(f"Welche News gibt es aktuell für den Nutzer?", schedule_user_data[user_id])
        try:
            await bot.send_message(chat_id=user_id, text=markdownify(ai_response), parse_mode="MarkdownV2")
            USER_DATA[user_id]["chat_history"].append({"role": "assistant", "content": ai_response})
        except Exception as e:
            logging.error(f"Fehler beim Senden an {user_id}: {e}")



def my_scheduler():
    scheduler = AsyncIOScheduler()

    morning_cron = CronTrigger(hour=7, minute=0)
    scheduler.add_job(weather_job, morning_cron, misfire_grace_time=60)

    noon_cron = CronTrigger(hour=12, minute=0)
    scheduler.add_job(weather_forecast_job, noon_cron, misfire_grace_time=60)

    lunch_cron = CronTrigger(hour=14, minute=0)
    scheduler.add_job(energy_prices_job, lunch_cron, misfire_grace_time=60)

    hourly_cron = CronTrigger(hour="6-22", minute=0)
    scheduler.add_job(dwd_warning_job, hourly_cron, misfire_grace_time=60)

    trash_cron = CronTrigger(hour=19, minute=0)
    scheduler.add_job(tomorrow_trash_job, trash_cron, misfire_grace_time=60)

    reminder_cron = CronTrigger(minute="1-59/5")
    scheduler.add_job(reminder_job, reminder_cron, misfire_grace_time=60)

    news_cron = CronTrigger(hour="6,18", minute=0)
    scheduler.add_job(news_job, news_cron, misfire_grace_time=60)

#     async def test_job():
#         logging.info("Test-Job fired!")
# 
#     test_cron = CronTrigger(minute="*/5")
#     scheduler.add_job(test_job, test_cron, misfire_grace_time=60)

    return scheduler
