# CONTENT

# import libs

# scrape heartbach cam for images
    # scrape conditions from:
    # (1) same url, easy but basic information (no swell period) 
    # (2) scrape by API request to stormglass API. Includes swell period but not tide information
    # (3) scrape from API that heartbeach uses. This API is ellegal but includes tidal data, hence all data that we (ideally) want.
# COMMENT: tidal data can later be added if we keep track of datetime, so not super important to collect now, stormglass it is. 
# if we include tide information, we shhould really make 4 tide groups, low-mid(lm),mid-high(mh),high-mid(hm),mid-low(ml). We need to create some sort of logic to calculate this
# setup filename, that should include swellheight_swellperiod(optional)_winddirection_windspeed_optional(tide)_datetime
# what we can include in the filename depends on the API method. 
# with filename we need some sort of logic that if a file already exists, we need to save it bi increasing a counter or something. 

# SCHEDULE
# (1) some sort of cronjob (but in  windows = Schedule?) that activates the script at certain time intervals
# (2) schedule logic should be in the script, and the script should therefore run continuously, but only does things every hour. 

import time
import os
import logging
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
from io import BytesIO
import requests
import arrow

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("surf_conditions.log"),
        logging.StreamHandler()
    ]
)

# Ensure the 'data' folder exists
os.makedirs("data", exist_ok=True)
max_duration = timedelta(hours=10)
start_time = datetime.now()

# Selenium setup for headless Chrome
def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://bit.ly/4gAqzaq")  # Webcam URL
    time.sleep(5)  # Allow time for the page to load
    return driver


def load_api_key(file_path: str = '.localsecret') -> str:
    """Load the API key from a file."""
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        raise Exception("API key file not found. Ensure '.localsecret' exists.")

# Fetch meteorological data from Stormglass
def fetch_meteo_data(APIKEY: str) -> list:
    start = arrow.utcnow()
    end = start.shift(hours=1)
    try:
        response = requests.get(
            'https://api.stormglass.io/v2/weather/point',
            params={
                'lat': 52.1035389,
                'lng': 4.2611759,
                'params': ','.join(['waveHeight', 'wavePeriod', 'waveDirection', 'windDirection', 'windSpeed']),
                'start': start.to('UTC').timestamp(),
                'end': end.to('UTC').timestamp()
            },
            headers={'Authorization': APIKEY}
        )
        response.raise_for_status()
        json_data = response.json()
        logging.info("Successfully fetched meteo data.")
    except requests.RequestException as e:
        logging.error(f"Error fetching data from Stormglass API: {e}")
        return ["FF", "FF", "FF", "FF", "FF"]

    data = json_data['hours'][1]
    wave_direction_num = data['waveDirection'].get('fcoo', "FF")
    wave_direction = degrees_to_dir16(wave_direction_num) if wave_direction_num != "FF" else "FF"
    wave_height = data['waveHeight'].get('fcoo', "FF")
    wave_period = data['wavePeriod'].get('fcoo', "FF")
    wind_direction_num = data['windDirection'].get('noaa', "FF")
    wind_direction = degrees_to_dir16(wind_direction_num) if wind_direction_num != "FF" else "FF"
    wind_speed = data['windSpeed'].get('noaa', "FF")
    return [wave_direction, wave_height, wave_period, wind_direction, wind_speed]

# Convert degrees to 16-point compass direction
def degrees_to_dir16(degrees: float) -> str:
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                  "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    idx = int((degrees + 11.25) % 360 / 22.5)
    return directions[idx]

# Create a filename based on meteorological data
def create_filename(timestamp: str, list_of_params: list) -> str:
    wave_direction, wave_height, wave_period, wind_direction, wind_speed = list_of_params
    wind_speed_formatted = f"{float(wind_speed) * 3.6:.1f}kmh" if wind_speed != "FF" else "FF"
    return f"{wave_direction}_{wave_height}m_{wave_period}s_{wind_direction}_{wind_speed_formatted}_{timestamp}.png"

# Capture screenshots with 12-second intervals
def capture_screenshots(driver, meteo_params):
    for i in range(8):
        try:
            screenshot = driver.get_screenshot_as_png()
            image = Image.open(BytesIO(screenshot))
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/{create_filename(timestamp, meteo_params)}"
            image.save(filename)
            logging.info(f"Screenshot {i+1} saved as {filename[5:]}")
        except Exception as e:
            logging.error(f"Error taking screenshot {i+1}: {e}")
        if i < 7:
            time.sleep(12)

# Heartbeat logger during long waits
def wait_until_next_hour():
    next_capture_time = datetime.now() + timedelta(minutes=60) - timedelta(seconds=8 * 12)
    while datetime.now() < next_capture_time:
        logging.info("Waiting until next capture cycle... Script is still running.")
        time.sleep(300)  # Heartbeat every 5 minutes during wait

# Slimmed-down main function
def main():
    logging.info("Starting the screenshot capture process.")
    driver = setup_driver()
    APIKEY = load_api_key()
    try:
        while datetime.now() - start_time < max_duration:
            meteo_params = fetch_meteo_data(APIKEY)
            capture_screenshots(driver, meteo_params)
            wait_until_next_hour()
    except Exception as e:
        logging.error(f"Error during the screenshot capture process: {e}")
    finally:
        driver.quit()
        logging.info("Script finished, browser closed.")

if __name__ == "__main__":
    main()
