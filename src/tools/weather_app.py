import os, asyncio, json
import requests
import datetime, pytz
from typing import Annotated


async def get_weather_week(
    ) -> Annotated[str, "Return the weather forecast for the next three days."]:
    """
    Return weather forecast for the next three days. Data included are: temperature, weather, clouds, and wind at 3-hour interval. Additionally sunrise and sunset times are included.
    """
    latitude, longitude = os.getenv("HOME_LATITUDE"), os.getenv("HOME_LONGITUDE")

    uri = "https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API key}&units=metric"
    uri = uri.replace("{lat}", str(latitude)).replace("{lon}", str(longitude))
    uri = uri.replace("{API key}", os.getenv("OPENWEATHER_API_KEY"))

    response = await asyncio.to_thread(requests.get, uri)
    response.raise_for_status()

    response = response.json()

    result = dict()
    timezone = pytz.timezone("Europe/Berlin")

    result["current_datetime"] = datetime.datetime.now(tz=timezone).strftime("%Y-%m-%d %H:%M")
    result["sunrise"] = datetime.datetime.fromtimestamp(response["city"]["sunrise"], tz=timezone).strftime("%H:%M")
    result["sunset"] = datetime.datetime.fromtimestamp(response["city"]["sunset"], tz=timezone).strftime("%H:%M")
    count = 0
    for entry in response["list"]:
        result_entry = dict()
        result_entry["temp"] = entry["main"]["temp"]
        result_entry["weather"] = entry["weather"][0]["main"]
        result_entry["clouds"] = entry["clouds"]["all"]
        result_entry["wind"] = entry["wind"]["speed"]

        dt = datetime.datetime.fromtimestamp(entry["dt"], tz=timezone)
        result[dt.strftime("%Y-%m-%d %H:%M")] = result_entry
        count += 1
        if count >= 25:
            break
    
    result["system-instruction"] = "Please write a proper text summary for the weather forecast for the next three days. If possible, do not use bullet points. Instead write a short and concise flowing text that is easy to read."

    return json.dumps(result)


async def get_weather_today(
    ) -> Annotated[str, "Return the weather forecast for today."]:
    """
    Return weather forecast for the remainder of today. Data included are: temperature, weather, clouds, and wind at 3-hour interval. Additionally sunrise and sunset times are included.
    """
    result = await get_weather_week()
    timezone = pytz.timezone("Europe/Berlin")
    current_date = datetime.datetime.now(tz=timezone).strftime("%Y-%m-%d")

    today_results = dict()
    today_results["current_datetime"] = result["current_datetime"]
    today_results["sunrise"] = result["sunrise"]
    today_results["sunset"] = result["sunset"]
    for k, v in result.items():
        if k.startswith(current_date):
            today_results[k] = v
    
    today_results["system-instruction"] = "Please write a proper text summary for the weather forecast for today. If possible, do not use bullet points. Instead write a short and concise flowing text that is easy to read."

    return json.dumps(today_results)


if __name__ == "__main__":
    # result = asyncio.run(get_weather_week())
    pass

    result_today = asyncio.run(get_weather_today())
    pass