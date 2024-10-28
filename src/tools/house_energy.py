import os, json, requests, asyncio
from datetime import datetime
from typing import Annotated


EVCC_URI=os.getenv("EVCC_URI")

async def get_energy_house_data() -> Annotated[str, "The current energy data of the house."]:
    """
    Returns the current energy data of the house including current energy consumption, pv energy production, wallbox energy production and battery soc. Negative values mean that the battery is charged or power is fed to the grid.
    """
    url = EVCC_URI + "/api/state"
    response = await asyncio.to_thread(requests.get, url)
    response.raise_for_status()

    response = response.json()

    
    result = dict()
    result["battery"] = response["result"]["battery"]
    result["batteryPower"] = response["result"]["battery"][0]["power"]
    result["batterySoC"] = response["result"]["battery"][0]["soc"]
    result["batteryCapacity"] = str(response["result"]["battery"][0]["capacity"]) + " kWh"
    result["gridPower"] = response["result"]["gridPower"]
    result["homePower"] = response["result"]["homePower"]
    result["pvPower"] = response["result"]["pvPower"]
    result["wallboxPower"] = response["result"]["loadpoints"][0]["chargePower"]
    return json.dumps(result)


async def get_energy_prices() -> Annotated[str, "A list of hourly energy prices from the grid."]:
    """ 
    Returns a list of energy prices in Euro from the grid for each hour till 12:00 today or tomorrow.
    """
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M")
    url = EVCC_URI + "/api/tariff/grid"
    response = await asyncio.to_thread(requests.get, url)
    response.raise_for_status()
    response_obj = dict()
    response_obj["data"]= response.json()
    response_obj["current-datetime"] = current_time + " " + current_date
    response_obj["system-instruction"] = "Please report the local minimum and maximum prices in a range of 2-5 cents and according time ranges to the user for loading the electric vehicle."
    return json.dumps(response_obj)


async def set_wallbox_mode(
        mode: Annotated[str, "Einer der folgenden Werte: {'off', 'pv', 'minpv', 'now'}. Dabei bedeutet 'off' das Laden deaktiviert ist, 'pv' das Laden nur mittels PV-Überschuss erfolgt, 'minpv' das Laden mit minimaler Leistung erfolgt, aber mit PV-Überschuss ergänzt wird (sofern vorhanden) und 'now' das Laden sofort mit maximaler Leistung erfolgt."] = None
    ) -> Annotated[str, "Der aktuelle Modus der Wallbox."]:
    """
    Setzt den Modus der Wallbox oder fragt den aktuellen Modus ab, wenn kein Modus übergeben wird.
    """
    # Wenn ein Modus übergeben wird, setzen wir diesen
    url = EVCC_URI + "/api/loadpoints/1/mode/${MODE}".replace("${MODE}", mode)
    response = await asyncio.to_thread(requests.post, url)
    return response.json()


async def get_wallbox_status() -> Annotated[str, "Der aktuelle Status der Wallbox."]:
    """
    Fragt den aktuellen Status der Wallbox ab. Dabei ist der Modus einer der folgenden Werte: {'off', 'pv', 'minpv', 'now'}. Dabei bedeutet 'off' das Laden deaktiviert ist, 'pv' das Laden nur mittels PV-Überschuss erfolgt, 'minpv' das Laden mit minimaler Leistung erfolgt, aber mit PV-Überschuss ergänzt wird (sofern vorhanden) und 'now' das Laden sofort mit maximaler Leistung erfolgt."
    """
    url = EVCC_URI + "/api/state"
    response = await asyncio.to_thread(requests.get, url)
    r = json.loads(response.text)
    result_mode = r["result"]["loadpoints"][0]["mode"]
    result_charging = r["result"]["loadpoints"][0]["charging"]
    result_power = r["result"]["loadpoints"][0]["chargePower"]
    return json.dumps({"mode": result_mode, "charging": result_charging, "power": result_power})


WASH_URI=os.getenv("WASH_URI")

async def get_washing_machine_status():
    """
    Returns the status of the washing machine. Can be either 'washing', 'idle' or 'off'.
    """
    washingResponse = await asyncio.to_thread(requests.get, WASH_URI + "/rpc/Shelly.GetStatus", timeout=3)
    washingResponse.raise_for_status()
    washingResponse = json.loads(washingResponse.text)
    washingReading = washingResponse["switch:0"]["apower"]
    if washingReading < 1.0:
        return json.dumps({"status": "off"})
    if washingReading < 10.0:
        return json.dumps({"status": "idle"})
    return json.dumps({"status": "washing"})


DRY_URI=os.getenv("DRY_URI")

async def get_dryer_machine_status():
    """
    Returns the status of the dryer. Can be either 'drying', 'idle' or 'off'.
    """
    dryerResponse = await asyncio.to_thread(requests.get, DRY_URI + "/rpc/Shelly.GetStatus", timeout=3)
    dryerResponse.raise_for_status()
    dryerResponse = json.loads(dryerResponse.text)
    dryerReading = dryerResponse["switch:0"]["apower"]
    if dryerReading < 1.0:
        return json.dumps({"status": "off"})
    if dryerReading < 10.0:
        return json.dumps({"status": "idle"})
    return json.dumps({"status": "drying"})



if __name__ == "__main__":

    # dryer = asyncio.run(get_dryer_machine_status())

    # wallbox_status = asyncio.run(get_wallbox_status())

    energy_data = asyncio.run(get_energy_house_data())

    energy_prices = asyncio.run(get_energy_prices())
    
    pass