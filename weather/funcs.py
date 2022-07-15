"""Functions for use by models.py and views.py"""
import requests
import json
from pathlib import Path
from datetime import datetime

from django.conf import settings

BASE_DIR = Path(__file__).resolve().parent.parent
ICONS_URL = 'static/media/images/icons/'
ICONS_DIR = BASE_DIR.joinpath(ICONS_URL)

def get_all_timezones():
    """Read timezone mappings from JSON file"""
    file_path = BASE_DIR.joinpath('static/weather/timezones.json')
    with open(file_path) as f:
        timezones = json.load(f)
    return timezones

def get_timezone(lat, long):
    """Get timezone for latitude/longitude pair from Google Time Zones API"""
    base_url = "https://maps.googleapis.com/maps/api/timezone/json?"
    params = {'location': f'{lat},{long}',
              'timestamp': str(int(datetime.timestamp(datetime.now()))),
              'key': settings.GOOGLE_API_KEY}
    response = requests.get(base_url, params)
    if response.status_code == 200:
        try:
            return response.json()["timeZoneId"]
        except KeyError:
            print('KeyError accessing Google Timezone response. Default to EST')
            return 'America/New_York'
    else:
        print('Google Timezone API Request failed. Default to EST')
        return 'America/New_York'

def get_codes():
    """Read mappings from JSON file of weather codes > weather descriptions"""
    file_path = BASE_DIR.joinpath('static/weather/codes.json')
    with open(file_path) as f:
        codes = json.load(f)
    return codes['weatherCode'], codes['weatherCodeDay']

def get_icon_path(code: str) -> str:
    """Retrieve the relative path to the weather icon for a given code"""
    try:
        icon_path_abs = next(ICONS_DIR.glob(f'{code}*.png'))
    except:
        return ''
    return icon_path_abs.relative_to(BASE_DIR / 'static/media/').__str__
