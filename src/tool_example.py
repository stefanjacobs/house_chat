import os
import requests
from src.tool_def_generator import ToolDefGenerator

EVCC_URI=os.getenv("EVCC_URI")


def get_energy_house_data():
    """
    Returns the current energy data of the house including current consumption, pv readings and battery soc.
    """
    url = EVCC_URI + "/api/state"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_energy_prices():
    """ 
    Returns a list of energy prices in Euro from the grid for each hour till 12:00 today or tomorrow.
    """
    url = EVCC_URI + "/api/tariff/grid"
    response = requests.get(url)
    response.raise_for_status()
    response_obj = dict()
    response_obj["data"]= response.json()
    response_obj["system-instruction"] = "Please report the local minimum and maximum prices and according time ranges to the user."
    return response_obj


import requests
from typing import Annotated, Optional

def set_or_get_wallbox_mode(
        mode: Annotated[Optional[str], "Einer der folgenden Werte: {'off', 'pv', 'minpv', 'now'}. Dabei bedeutet 'off' das Laden deaktiviert ist, 'pv' das Laden nur mittels PV-Überschuss erfolgt, 'minpv' das Laden mit minimaler Leistung erfolgt, aber mit PV-Überschuss ergänzt wird (sofern vorhanden) und 'now' das Laden sofort mit maximaler Leistung erfolgt."] = None
    ) -> Annotated[str, "Der aktuelle Modus der Wallbox."]:
    """
    Setzt den Modus der Wallbox oder fragt den aktuellen Modus ab, wenn kein Modus übergeben wird.
    """
    if mode:
        # Wenn ein Modus übergeben wird, setzen wir diesen
        url = EVCC_URI + "/api/loadpoints/1/mode/${MODE}".replace("${MODE}", mode)
        response = requests.post(url)
        return response.json()
    else:
        # Wenn kein Modus übergeben wird, fragen wir den aktuellen Modus ab
        url = EVCC_URI + "/api/state"
        response = requests.get(url)
        r = json.loads(response.text)
        result_mode = r["result"]["loadpoints"][0]["mode"]
        return {"mode": result_mode}


def get_wallbox_status() -> Annotated[str, "Der aktuelle Status der Wallbox."]:
    """
    Fragt den aktuellen Status der Wallbox ab.
    """
    url = EVCC_URI + "/api/state"
    response = requests.get(url)
    r = json.loads(response.text)
    result_mode = r["result"]["loadpoints"][0]["mode"]
    result_charging = r["result"]["loadpoints"][0]["charging"]
    result_power = r["result"]["loadpoints"][0]["chargePower"]
    return {"mode": result_mode, "charging": result_charging, "power": result_power}


WASH_URI=os.getenv("WASH_URI")

import json

def get_washing_machine_status():
    """
    Returns the status of the washing machine. Can be either 'washing', 'idle' or 'off'.
    """
    washingResponse = requests.get(WASH_URI + "/rpc/Shelly.GetStatus", timeout=3)
    washingResponse.raise_for_status()
    washingResponse = json.loads(washingResponse.text)
    washingReading = washingResponse["switch:0"]["apower"]
    if washingReading < 1.0:
        return {"status": "off"}
    if washingReading < 10.0:
        return {"status": "idle"}
    return {"status": "washing"}


DRY_URI=os.getenv("DRY_URI")

def get_dryer_machine_status():
    """
    Returns the status of the dryer. Can be either 'drying', 'idle' or 'off'.
    """
    dryerResponse = requests.get(DRY_URI + "/rpc/Shelly.GetStatus", timeout=3)
    dryerResponse.raise_for_status()
    dryerResponse = json.loads(dryerResponse.text)
    dryerReading = dryerResponse["switch:0"]["apower"]
    if dryerReading < 1.0:
        return {"status": "off"}
    if dryerReading < 10.0:
        return {"status": "idle"}
    return {"status": "drying"}


import uuid
from typing import List, Dict, Optional
from datetime import datetime

# TODO for later: Not In-memory storage for todos
todos: Dict[str, List[Dict[str, Optional[str]]]] = {}

# Helper function to generate a unique ID for each todo
def generate_todo_id() -> str:
    """
    Generates a unique ID for each todo item.
    
    :return: A string representing a unique ID.
    """
    return str(uuid.uuid4())

def get_todos_by_category(category: str = "todo") -> str: # List[Dict[str, Optional[str]]]:
    """
    Retrieves all todos for a given category.
    :param category: The category of todos to retrieve. Defaults to "todo".
    :return: A list of todos in the given category.
    """
    return str(todos.get(category, []))


def add_todo(todo: str, category: str = "todo", completed_date: Optional[str] = None) -> str:
    """
    Adds a todo item to a specific category.
    :param todo: The todo item description.
    :param category: The category to which the todo item should be added. Defaults to "todo".
    :param completed_date: The optional completed date of the todo item.
    :return: The ID of the added todo item.
    """
    if category not in todos:
        todos[category] = []
    
    todo_id = generate_todo_id()
    todos[category].append({
        'id': todo_id,
        'todo': todo,
        'completed_date': completed_date
    })
    
    return str(todo_id)

def delete_todo_by_id(todo_id: str, category: str = "todo") -> str:
    """
    Deletes a todo item from a specific category by its ID.
    :param todo_id: The ID of the todo item to delete.
    :param category: The category from which to delete the todo. Defaults to "todo".
    :return: True if the todo was found and deleted, False otherwise.
    """
    if category in todos:
        original_length = len(todos[category])
        todos[category] = [item for item in todos[category] if item['id'] != todo_id]
        
        return str(len(todos[category]) < original_length)
    return str(False)

def get_categories() -> str:
    """
    Retrieves the list of all categories.
    :return: A list of all category names.
    """
    return str(list(todos.keys()))

def delete_category(category: str) -> str:
    """
    Deletes a category and all its associated todos.
    :param category: The category to delete.
    :return: True if the category existed and was deleted, False otherwise.
    """
    if category in todos:
        del todos[category]
        return str(True)
    return str(False)

from typing import Annotated, Optional

def todo_app_api(
    op: Annotated[str, "The operation to perform. One of 'add', 'delete', 'get', 'categories', 'delete_category'"], 
    todo: Annotated[Optional[str], "The todo item description"] = None, 
    category: Annotated[Optional[str], "The category of the todo item"] = None, 
    completed_date: Annotated[Optional[str], "The completed date of the todo item"] = None, 
    todo_id: Annotated[Optional[str], "The ID of the todo item to delete"] = None
    ) -> Annotated[str, "A response message based on the operation."]:
    """
    A simple API for managing todo items.
    """
    if op == 'add':
        if todo is None:
            return "Error: 'todo' parameter is required for 'add' operation."
        return add_todo(todo, category, completed_date)
    elif op == 'delete':
        if todo_id is None:
            return "Error: 'todo_id' parameter is required for 'delete' operation."
        return delete_todo_by_id(todo_id, category)
    elif op == 'get':
        return get_todos_by_category(category)
    elif op == 'categories':
        return get_categories()
    elif op == 'delete_category':
        if category is None:
            return "Error: 'category' parameter is required for 'delete_category' operation."
        return delete_category(category)
    else:
        return "Error: Invalid operation. Supported operations: 'add', 'delete', 'get', 'categories', 'delete_category'."











generator = ToolDefGenerator()
TOOLS = generator.generate(get_energy_house_data, set_or_get_wallbox_mode, get_wallbox_status, get_dryer_machine_status, get_washing_machine_status, todo_app_api)
