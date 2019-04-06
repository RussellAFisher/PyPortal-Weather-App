"""
This example queries the Open Weather Maps site API to find out the current
weather for your location... and display it on a screen!
if you can find something that spits out JSON data, we can display it
"""
import sys
import time
import board
import busio
from adafruit_pyportal import PyPortal
cwd = ("/"+__file__).rsplit('/', 1)[0] # the current working directory (where this file is)
sys.path.append(cwd)
import openweather_graphics  # pylint: disable=wrong-import-position
from analogio import AnalogIn
from digitalio import DigitalInOut

# Get wifi details and more from a secrets.py file
from secrets import secrets

# Import ADT7410 Library
import adafruit_adt7410

ZIP = 80206

# Use cityname, country code where countrycode is ISO3166 format.
# E.g. "New York, US" or "London, GB"
LOCATION = "Denver, US"

# Set up where we'll be fetching data from
WEATHER_DATA_SOURCE = "http://api.openweathermap.org/data/2.5/weather?q=" + LOCATION
WEATHER_DATA_SOURCE += "&appid=" + secrets['openweather_token']
# You'll need to get a token from openweather.org, looks like 'b6907d289e10d714a6e88b30761fae22'
WEATHER_DATA_LOCATION = []


# Initialize the pyportal object and let us know what data to fetch and where
# to display it
pyportal = PyPortal(url=WEATHER_DATA_SOURCE,
                    json_path=WEATHER_DATA_LOCATION,
                    status_neopixel=board.NEOPIXEL,
                    default_bg=0x9900FF)

gfx = openweather_graphics.OpenWeather_Graphics(pyportal.splash, am_pm=True)

# Set up an analog light sensor on the PyPortal
adc = AnalogIn(board.LIGHT)

localtile_refresh = None
weather_refresh = None
while True:
    print(adc.value)

    # set brightness based on room brightness, min 20% max 80%
    brightnessPercent = adc.value/65536
    if brightnessPercent < .2:
        brightnessPercent = .2
    elif brightnessPercent > .8:
        brightnessPercent = .8

    pyportal.set_backlight(brightnessPercent)

    # only query the online time once per hour (and on first run)
    if (not localtile_refresh) or (time.monotonic() - localtile_refresh) > 3600:
        try:
            pyportal.get_local_time()
            localtile_refresh = time.monotonic()
        except RuntimeError as e:
            print("Some error occured, retrying! -", e)
            continue

    # only query the weather every 10 minutes (and on first run)
    if (not weather_refresh) or (time.monotonic() - weather_refresh) > 600:
        try:
            value = pyportal.fetch()
            print("Response is", value)
            gfx.display_weather(value)
            weather_refresh = time.monotonic()
        except RuntimeError as e:
            print("Some error occured, retrying! -", e)
            continue

    gfx.update_time()
    time.sleep(30)  # wait 30 seconds before updating anything again
