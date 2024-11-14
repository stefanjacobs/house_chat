import os
from typing import Annotated
from weconnect import weconnect
import json


class CarApp:
    
    def __init__(self):
        self.VW_USERNAME=os.getenv("VW_USER")
        self.VW_PASSWORD=os.getenv("VW_PASS")
        self.VW_VIN=os.getenv("VW_VIN")
        self.connection = weconnect.WeConnect(username=self.VW_USERNAME, password=self.VW_PASSWORD, updateAfterLogin=False, loginOnInit=True, maxAge=600)

    
    def get_car_status(self):
        self.connection.update(updatePictures=False, updateCapabilities=False)
        return self.connection.vehicles[self.VW_VIN]


carApp = CarApp()


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




if __name__ == "__main__":
    status = get_car_status()
    pass
