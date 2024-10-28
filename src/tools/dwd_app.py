
# TODO: Implement the DWD api and cache the results for 3 hours

import os, datetime, logging
from dwdwfsapi import DwdWeatherWarningsAPI

LATITUDE = os.getenv("HOME_LATITUDE")
LONGITUDE = os.getenv("HOME_LONGITUDE")
DWD = DwdWeatherWarningsAPI((LATITUDE, LONGITUDE))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


def update():
    global DWD, LATITUDE, LONGITUDE
    minVisLevel = 3 # step["vis-min-level"] #     vis-min-level: 3 # warning levels between 0 and 4

    now = datetime.datetime.now(datetime.timezone.utc)
    try:
        if now - DWD.last_update > datetime.timedelta(minutes=15):
            DWD.update()
    except:
        DWD = DwdWeatherWarningsAPI((LATITUDE, LONGITUDE))
        return False
    
    if not DWD.data_valid:
        return False
    
    headlines, color, maxLevel = "", None, -1

    for warning in DWD.expected_warnings:
        if warning["level"] >= minVisLevel:
            headlines += warning["event"] + " - "
            if warning["level"] > maxLevel:
                color = warning["color"]
                maxLevel = warning["level"]

    for warning in DWD.current_warnings:
        if warning["level"] >= minVisLevel:
            headlines += warning["event"] + " - "
            if warning["level"] > maxLevel:
                color = warning["color"]
                maxLevel = warning["level"]
    
    if headlines != "":
        headlines = headlines[0:-2]
        # updateUlanzi(config, headlines, color)
        return True
    
    return False



if __name__ == "__main__":
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
