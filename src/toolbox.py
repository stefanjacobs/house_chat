
from src.tools.house_energy import get_energy_house_data, set_wallbox_mode, get_wallbox_status, get_dryer_machine_status, get_washing_machine_status, get_energy_prices
from src.tools.trash_app import get_tomorrows_trash, get_todays_trash, get_next_trash
from src.tools.weather_app import get_weather_week, get_weather_today
from src.tools.dwd_app import get_current_warnings
from src.tools.car_app import get_car_status, car_climate_control
from src.tools.todo_app import get_overdue_todos, create_todo, get_categories, get_todos_by_category, update_todo, get_open_todos
from src.tools.news_app import get_news

from src.tool_def_generator import ToolDefGenerator

generator = ToolDefGenerator()

TOOLBOX = generator.generate(get_energy_house_data, set_wallbox_mode, get_wallbox_status, get_dryer_machine_status, get_washing_machine_status, get_energy_prices, get_todays_trash, get_tomorrows_trash, get_next_trash, get_weather_today, get_weather_week, get_current_warnings, get_car_status, get_overdue_todos, create_todo, get_categories, get_todos_by_category, update_todo, get_open_todos, get_news, car_climate_control)
