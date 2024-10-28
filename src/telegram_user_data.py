import datetime
from src.ai_prompts import get_sysprompt


USER_DATA = {}


async def create_user_data(user_id):
    """
    Erstellt ein Nutzerdatenobjekt
    """
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.datetime.now().strftime("%H:%M")
    USER_DATA[user_id] = {
        "user_id": user_id,
        "chat_history": [
            {"role": "system", "content": get_sysprompt(current_date, current_time)}
        ]
    }


async def reset_history(user_id):
    """
    Setze die chat_history des Nutzers zurück
    """
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.datetime.now().strftime("%H:%M")
    USER_DATA[user_id] = {
        "user_id": user_id,
        "chat_history": [
            {"role": "system", "content": get_sysprompt(current_date, current_time)}
        ]
    }
