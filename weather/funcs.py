"""Functions for use by models.py and views.py"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def get_timezones():
    """Read timezone mappings from JSON file"""
    file_path = BASE_DIR.joinpath('static/weather/timezones.json')
    with open(file_path) as f:
        timezones = json.load(f)
    return timezones

def get_codes():
    """Read weather code mappings from JSON file"""
    file_path = BASE_DIR.joinpath('static/weather/codes.json')
    with open(file_path) as f:
        codes = json.load(f)
    return codes['weatherCodeDay']
