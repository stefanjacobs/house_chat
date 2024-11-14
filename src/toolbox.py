
from src.tools.house_energy import get_energy_house_data, set_wallbox_mode, get_wallbox_status, get_dryer_machine_status, get_washing_machine_status, get_energy_prices
from src.tools.trash_app import get_tomorrows_trash, get_todays_trash, get_next_trash
from src.tools.weather_app import get_weather_week, get_weather_today
from src.tools.dwd_app import get_current_warnings
from src.tools.car_app import get_car_status
from src.tools.todo_app import todo_app_api

from src.tool_def_generator import ToolDefGenerator

generator = ToolDefGenerator()
TOOLBOX = generator.generate(get_energy_house_data, set_wallbox_mode, get_wallbox_status, get_dryer_machine_status, get_washing_machine_status, todo_app_api, get_energy_prices, get_todays_trash, get_tomorrows_trash, get_next_trash, get_weather_today, get_weather_week, get_current_warnings, get_car_status)
