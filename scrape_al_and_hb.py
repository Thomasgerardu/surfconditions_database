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
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("surf_conditions.log"),
        logging.StreamHandler()
    ]
)

# Folders and urls
os.makedirs("data_aloha", exist_ok=True)
os.makedirs("data_heartbeach", exist_ok=True)
aloha_yt_url = "https://www.youtube.com/embed/XB2T9RjIM-g?autoplay=1&fs=1&rel=0&modestbranding=1&mute=1&vq=hd1080"
heartbeach_yt_url = "https://www.youtube.com/embed/8nn9fAr9LCE?autoplay=1&mute=1&rel=0&showinfo=0&vq=hd1080"
tide_file_path = r"C:/Github/surfconditions_database/hwlw-SCHEVNGN-20240101-20241231.xml"
max_duration = timedelta(hours=10)
start_time = datetime.now()

#%% Supporting funcs

def setup_driver(url):
    # Selenium setup for headless Chrome
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    time.sleep(5)  # Allow time for the page to load
    return driver


def load_api_key(file_path: str = '.localsecret') -> str:
    # Load the API key from a file.
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        raise Exception("API key file not found. Ensure '.localsecret' exists.")

def degrees_to_dir16(degrees: float) -> str:
    # Convert degrees to 16-point compass direction
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                  "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    idx = int((degrees + 11.25) % 360 / 22.5)
    return directions[idx]


def create_filename(timestamp: str, list_of_params: list, tideregime: str, identifier: str) -> str:
    # Create a filename based on meteorological data
    wave_direction, wave_height, wave_period, wind_direction, wind_speed = list_of_params
    wind_speed_formatted = f"{float(wind_speed) * 3.6:.1f}kmh" if wind_speed != "FF" else "FF"
    return f"{wave_direction}_{wave_height}m_{wave_period}s_{wind_direction}_{wind_speed_formatted}_{tideregime}_{timestamp}_{identifier}.png"


def wait_until_next_hour(start_time):
    """
    Wait until the next capture cycle begins, subtracting the script execution time from the wait duration.
    """
    elapsed_time = datetime.now() - start_time
    next_capture_time = start_time + timedelta(minutes=60)
    remaining_time = (next_capture_time - datetime.now()).total_seconds()

    if remaining_time > 0:
        logging.info(f"Waiting for {remaining_time // 60:.0f} minutes and {remaining_time % 60:.0f} seconds until the next capture cycle.")
        time.sleep(remaining_time)
    else:
        logging.warning("Processing exceeded the one-hour cycle. Starting next cycle immediately.")




#%% Fetch from internet funcs

def fetch_meteo_data(APIKEY: str) -> list:
    # Fetch meteorological data from Stormglass
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

def capture_screenshots(driver, meteo_params, folder, identifier):
    # Fetch tide range
    tide_data = parse_tides(tide_file_path)
    current_tide_phase = find_current_tide_phase(tide_data)
    for i in range(50):
        try:
            screenshot = driver.get_screenshot_as_png()
            image = Image.open(BytesIO(screenshot))
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{folder}/{create_filename(timestamp, meteo_params, current_tide_phase, identifier)}"
            image.save(filename)
            logging.info(f"Screenshot {i+1} saved as {filename[len(folder)+1:]}")
        except Exception as e:
            logging.error(f"Unexpected error taking screenshot {i + 1}: {e}")
        if i < 49:
            time.sleep(3)



#%% Tide funs

def parse_tides(file_path):
    # Parse tide data from an XML file
    tree = ET.parse(file_path)
    root = tree.getroot()
    tide_data = []

    # Iterate over <value> elements to extract tide information
    for entry in root.find('values'):
        dt = datetime.strptime(entry.find('datetime').text.strip(), "%Y%m%d%H%M")
        tide = entry.find('tide').text.strip()  # HW or LW
        val = int(entry.find('val').text.strip())
        tide_data.append((dt, tide, val))

    # Sort by datetime to ensure order
    tide_data.sort(key=lambda x: x[0])
    return tide_data

def find_current_tide_phase(tide_data):
    # Find the current tide regime based on tide data
    now = datetime.now()
    
    # Find the nearest low and high tide before and after current time
    previous_tide = None
    next_tide = None
    
    for i in range(len(tide_data) - 1):
        if tide_data[i][0] <= now <= tide_data[i + 1][0]:
            previous_tide = tide_data[i]
            next_tide = tide_data[i + 1]
            break
    
    # If no surrounding tides found (boundary case), return None
    if not previous_tide or not next_tide:
        return None

    # Determine regime phase
    time_diff = (next_tide[0] - previous_tide[0]).total_seconds()
    elapsed_time = (now - previous_tide[0]).total_seconds()
    phase_position = elapsed_time / time_diff
    
    # Determine the tide regime based on the phase position
    if previous_tide[1] == "LW" and next_tide[1] == "HW":
        if phase_position < 0.5:
            return "lm"  # low-mid
        else:
            return "mh"  # mid-high
    elif previous_tide[1] == "HW" and next_tide[1] == "LW":
        if phase_position < 0.5:
            return "hm"  # high-mid
        else:
            return "ml"  # mid-low

def main():
    logging.info("Starting the screenshot capture process.")
    APIKEY = load_api_key()
    meteo_params = fetch_meteo_data(APIKEY)
    heartbeach_driver = setup_driver(heartbeach_yt_url)
    aloha_driver = setup_driver(aloha_yt_url)
    try:
        while datetime.now() - start_time < max_duration:
            cycle_start_time = datetime.now()
            capture_screenshots(heartbeach_driver, meteo_params, "data_heartbeach", "h")
            capture_screenshots(aloha_driver, meteo_params, "data_aloha", "a")
            wait_until_next_hour(cycle_start_time)
    except Exception as e:
        logging.error(f"Error during the screenshot capture process: {e}")
    finally:
        heartbeach_driver.quit()
        aloha_driver.quit()
        logging.info("Script finished, browsers closed.")

if __name__ == "__main__":
    main()