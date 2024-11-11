from typing import Annotated
import datetime, ics

# Get the current year
current_year = datetime.datetime.now().year

filename = "database/abfuhrtermine-" + str(current_year) + ".ics"
with open(filename, 'r') as file:
    data = file.read()
calendar = ics.Calendar(data)


async def get_tomorrows_trash(
    ) -> Annotated[str, "Return a list of trash bins that will be emptied tomorrow."]:
    """
    Return a list of trash bins that is going to be emptied tomorrow.
    """
    global calendar
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    trash = []
    for event in calendar.events:
        if event.begin.date() == tomorrow:
            if "gelb" in event.name.lower():
                trash.append("Gelbe Tonne")
            elif "restmülltonne" in event.name.lower():
                trash.append("Restmüll")
            elif "biotonne" in event.name.lower():
                trash.append("Biotonne")
            elif "papiertonne" in event.name.lower():
                trash.append("Papiertonne")
    return trash


async def get_todays_trash(
    ) -> Annotated[str, "Return a list of trash bins that will be emptied today."]:
    """
    Return a list of trash bins that is going to be emptied today.
    """
    global calendar
    today = datetime.date.today()
    trash = []
    for event in calendar.events:
        if event.begin.date() == today:
            if "gelb" in event.name.lower():
                trash.append("Gelbe Tonne")
            elif "restmülltonne" in event.name.lower():
                trash.append("Restmüll")
            elif "biotonne" in event.name.lower():
                trash.append("Biotonne")
            elif "papiertonne" in event.name.lower():
                trash.append("Papiertonne")
    return trash


async def get_next_trash(
) -> Annotated[str, "Return a list of trash bins and the date they will be emptied next."]:
    """
    Return a list of trash bins and the date they will be emptied next.
    """
    global calendar
    today = datetime.date.today()
    trash = []

    # Beginning from today, search the next trash events for each type of trash bin
    found = dict()
    for i in range(30):
        date = today + datetime.timedelta(days=i)
        for event in calendar.events:
            if event.begin.date() == date:
                if "gelb" in event.name.lower() and not found.get("gelb", False):
                    trash.append({"date": date, "type": "Gelbe Tonne"})
                    found["gelb"] = True
                elif "restmülltonne" in event.name.lower() and not found.get("restmülltonne", False):
                    trash.append({"date": date, "type": "Restmüll"})
                    found["restmülltonne"] = True
                elif "biotonne" in event.name.lower() and not found.get("biotonne", False):
                    trash.append({"date": date, "type": "Biotonne"})
                    found["biotonne"] = True
                elif "papiertonne" in event.name.lower() and not found.get("papiertonne", False):
                    trash.append({"date": date, "type": "Papiertonne"})
                    found["papiertonne"] = True
    
    return trash