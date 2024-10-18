import os, json, requests
import datetime


EVCC_URI=os.getenv("EVCC_URI")

def get_energy_house_data():
    """
    Returns the current energy data of the house including current energy consumption, pv energy production, wallbox energy production and battery soc.
    """
    url = EVCC_URI + "/api/state"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def get_energy_prices():
    """ 
    Returns a list of energy prices in Euro from the grid for each hour till 12:00 today or tomorrow.
    """
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M")
    url = EVCC_URI + "/api/tariff/grid"
    response = requests.get(url)
    response.raise_for_status()
    response_obj = dict()
    response_obj["data"]= response.json()
    response_obj["current-datetime"] = current_time + " " + current_date
    response_obj["system-instruction"] = "Please report the local minimum and maximum prices in a range of 2-5 cents and according time ranges to the user for loading the electric vehicle."
    return json.dumps(response_obj)


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
        return json.dumps({"mode": result_mode})


def get_wallbox_status() -> Annotated[str, "Der aktuelle Status der Wallbox."]:
    """
    Fragt den aktuellen Status der Wallbox ab. Dabei ist der Modus einer der folgenden Werte: {'off', 'pv', 'minpv', 'now'}. Dabei bedeutet 'off' das Laden deaktiviert ist, 'pv' das Laden nur mittels PV-Überschuss erfolgt, 'minpv' das Laden mit minimaler Leistung erfolgt, aber mit PV-Überschuss ergänzt wird (sofern vorhanden) und 'now' das Laden sofort mit maximaler Leistung erfolgt."
    """
    url = EVCC_URI + "/api/state"
    response = requests.get(url)
    r = json.loads(response.text)
    result_mode = r["result"]["loadpoints"][0]["mode"]
    result_charging = r["result"]["loadpoints"][0]["charging"]
    result_power = r["result"]["loadpoints"][0]["chargePower"]
    return json.dumps({"mode": result_mode, "charging": result_charging, "power": result_power})


WASH_URI=os.getenv("WASH_URI")

def get_washing_machine_status():
    """
    Returns the status of the washing machine. Can be either 'washing', 'idle' or 'off'.
    """
    washingResponse = requests.get(WASH_URI + "/rpc/Shelly.GetStatus", timeout=3)
    washingResponse.raise_for_status()
    washingResponse = json.loads(washingResponse.text)
    washingReading = washingResponse["switch:0"]["apower"]
    if washingReading < 1.0:
        return json.dumps({"status": "off"})
    if washingReading < 10.0:
        return json.dumps({"status": "idle"})
    return json.dumps({"status": "washing"})


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
        return json.dumps({"status": "off"})
    if dryerReading < 10.0:
        return json.dumps({"status": "idle"})
    return json.dumps({"status": "drying"})
