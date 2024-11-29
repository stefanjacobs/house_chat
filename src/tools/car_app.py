import os
from typing import Annotated, Optional
from weconnect import weconnect
from weconnect.elements.control_operation import ControlOperation
import json

from src.toolbox.toolbox import register_tool_decorator


class CarApp:
    
    def __init__(self):
        self.VW_USERNAME=os.getenv("VW_USER")
        self.VW_PASSWORD=os.getenv("VW_PASS")
        self.VW_VIN=os.getenv("VW_VIN")
        self.connection = weconnect.WeConnect(username=self.VW_USERNAME, password=self.VW_PASSWORD, updateAfterLogin=False, loginOnInit=True, maxAge=600)

    
    def get_car_status(self):
        self.connection.update(updatePictures=False, updateCapabilities=False)
        return self.connection.vehicles[self.VW_VIN]
    
    
    def car_climate_control(self, activate=None):
        print('#  update')
        self.connection.update(updatePictures=False, updateCapabilities=True)

        for vin, vehicle in self.connection.vehicles.items():
            if vin == self.VW_VIN:
                if "climatisation" in vehicle.domains \
                    and "climatisationStatus" in vehicle.domains["climatisation"] \
                    and vehicle.domains["climatisation"]["climatisationStatus"].enabled:
                    if vehicle.domains["climatisation"]["climatisationStatus"].climatisationState.enabled:
                        print('#  climatization status')
                        print(vehicle.domains["climatisation"]["climatisationStatus"].climatisationState.value)

                if vehicle.controls.climatizationControl is not None and vehicle.controls.climatizationControl.enabled:
                    if activate is None:
                        print('#  get climatization status')
                        print(vehicle.controls.climatizationControl.value)
                        return str(vehicle.controls.climatizationControl.value)
                    if activate == True:
                        print('#  start climatization')
                        vehicle.controls.climatizationControl.value = ControlOperation.START
                        return "Started climatization in car."
                    else:
                        print('#  stop climatization')
                        vehicle.controls.climatizationControl.value = ControlOperation.STOP
                        return "Stopped climatization in car."
        return "No climatization control available for this car."


carApp = CarApp()


@register_tool_decorator
def get_car_status() -> Annotated[str, "Return the current status of the car as a json string."]:
    """
    Generate status object for the given car and convert it to a dictionary.
    """
    global carApp
    status = carApp.get_car_status()

    result = dict()
    result["remaining-range-in-km"] = status.domains["measurements"]["rangeStatus"].electricRange.value
    result["battery-capacity-in-kwh"] = 80
    result["battery-soc-in-percent"] = status.domains["measurements"]["fuelLevelStatus"].currentSOC_pct.value
    result["odometer-in-km"] = status.domains["measurements"]["odometerStatus"].odometer.value
    result["parking-position-link"] = "https://www.google.com/maps/?q=" + str(status.domains["parking"]["parkingPosition"].latitude.value) + "," + str(status.domains["parking"]["parkingPosition"].longitude.value) 
    result["system-instruction"] = "Please write a proper text summary for the car status. If possible, do not use bullet points. Instead write a short and concise flowing text that is easy to read."
    
    return json.dumps(result)


@register_tool_decorator
def car_climate_control(
    activate: Annotated[Optional[str], "Activate or deactivate the car's climate control. 'True' for activate, 'False' for deactivate. If not given, return the current status of the climate control"] = None
) -> Annotated[str, "Returns a message that either indicates the status of the climate control. the climate control was activated or deactivated."]:
    """
    Activate or deactivate the car's climate control.
    """
    global carApp
    if activate is None or activate == "":
        result = carApp.car_climate_control(None)
    else:
        result = carApp.car_climate_control(activate == "True")
    return result



if __name__ == "__main__":
    status = get_car_status()
    pass
