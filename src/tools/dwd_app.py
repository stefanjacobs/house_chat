
# TODO: Implement the DWD api and cache the results for 3 hours

import os, datetime, logging
from dwdwfsapi import DwdWeatherWarningsAPI

LATITUDE = os.getenv("HOME_LATITUDE")
LONGITUDE = os.getenv("HOME_LONGITUDE")
DWD = DwdWeatherWarningsAPI((LATITUDE, LONGITUDE))
OLD_WARN = None




def update_dwd_cache():
    global DWD, LATITUDE, LONGITUDE

    # update the DWD cache every 55 minutes
    now = datetime.datetime.now(datetime.timezone.utc)
    try:
        if now - DWD.last_update > datetime.timedelta(minutes=55):
            DWD.update()
    except:
        DWD = DwdWeatherWarningsAPI((LATITUDE, LONGITUDE))

    # return True if the cached data is valid
    if not DWD.data_valid:
        return False
    return True


from typing import Annotated

def get_current_warnings(
    ) -> Annotated[str, "Return the current and expected weather warnings."]:
    """
    Return the current and expected weather warnings.
    """
    global DWD
    update_dwd_cache()

    cur_warn = "".join([str(warning) + "\n" for warning in DWD.current_warnings if warning["level"] >= 1])
    exp_warn = "".join([str(warning) + "\n" for warning in DWD.expected_warnings if warning["level"] >= 1])

    return str(DWD) + "\n" + "Current warnings:\n" + str(cur_warn) + "\nExpected warnings:\n" + str(exp_warn)


def check_new_warnings():
    global OLD_WARN

    if OLD_WARN is None:
        OLD_WARN = get_current_warnings()
        return False, ""
    
    new_warnings = get_current_warnings()
    if new_warnings != OLD_WARN:
        OLD_WARN = new_warnings
        logging.info(f"New warnings: {new_warnings}")
        return True, new_warnings
    
    return False, ""





if __name__ == "__main__":
    # Logging-Konfiguration für Debugging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
    )

    dwd = DWD
    dwd.update()
    logging.info(f"Warncell id: {dwd.warncell_id}")
    logging.info(f"Warncell name: {dwd.warncell_name}")
    logging.info(f"Number of current warnings: {len(dwd.current_warnings)}")
    logging.info(f"Current warning level: {dwd.current_warning_level}")
    logging.info(f"Number of expected warnings: {len(dwd.expected_warnings)}")
    logging.info(f"Expected warning level: {dwd.expected_warning_level}")
    logging.info(f"Last update: {dwd.last_update}")
    logging.info('-----------')
    for warning in dwd.current_warnings:
        logging.info(warning)
        logging.info('-----------')
    for warning in dwd.expected_warnings:
        logging.info(warning)
        logging.info('-----------')
    
    print()
    
    print(str(dwd))

    print()

    print(get_current_warnings())
