# Python libraries
from pathlib import Path
import requests
import json
from datetime import date, time, datetime, timedelta
import pytz
import calendar
# Django files
from django.shortcuts import  render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.utils.timezone import now  # default timezone = UTC
# Local files
from .models import Person, Weather, User_Person, Location
from .funcs import get_codes

# NOTE REGARDING TIMEZONES
# Timestamps are stored as UTC so should be compared to UTC time
# Dates and times of Weather data are stored in the local time zone

# Constants
BASE_DIR = Path(__file__).resolve().parent.parent
API_BASE_URL = 'https://api.tomorrow.io/v4/timelines'
API_KEY = 'P0upWa3NF5mlabyrkmlCDqZWDblfSUUc'
API_RESULT_LIFETIME = timedelta(hours=6)
WEATHER_CODES = get_codes()

# Helper functions for views
# =============================================================================
def api_request(weather: Weather, forecast_date: date, location: Location) -> Weather:
    """
    Issue an API request to obtain an updated weather forecast for the current
    date and the subsequent 2 days.
    
    :param weather: the current best result from the database, or None
    :param forecast_date: datetime.date object of the date needed
    :param location: Location object for the weather needed
    :return: a Weather object of the successful API or request or None
    """

    # convert forecast date into datetime with time=0:00
    if isinstance(forecast_date, datetime) == False:
        # startTime cannot be more than 6 hours in the past, so append the
        # the current local time to the forecast_date
        local_time = datetime.now(tz=pytz.timezone(location.timezone)).time()
        startTime = datetime.combine(forecast_date, local_time)
    elif isinstance(forecast_date, datetime):
        startTime = forecast_date
    else:
        print('> Log: forecast_date needs to be a date or datetime object')
        exit()

    lat_long = str(location.latitude) + ',' + str(location.longitude)
    params = {
        'location': lat_long,
        'startTime': startTime.isoformat() + 'Z',
        'endTime': (startTime + timedelta(days=3)).isoformat() + 'Z',
        'timesteps': '1d',
        'fields': ['temperature', 'weatherCodeDay'],
        'units': 'imperial',
        'apikey': API_KEY,
    }
    response = requests.get(API_BASE_URL, params)
    response_dict = response.json()
    if response.status_code == 200:
        # save json file for debugging and history
        out_directory = BASE_DIR.parent.joinpath('api-samples')
        out_filename = f"{location.name.lower().replace(' ', '-')}-1d-{forecast_date.isoformat()}-" \
                       f"{datetime.now().time().isoformat('seconds').replace(':','-')}.json"
        with open(out_directory.joinpath(out_filename), 'w') as f:
            json.dump(response_dict, f, indent=4)
        print(' > Log: saved API response to file:', {location.name}, {forecast_date})

        # now create Weather objects from API response, save, and return first
        # extract first interval (day) from response
        intervals = response_dict['data']['timelines'][0]['intervals']
        new_weathers = []
        for interval in intervals:
            date_iso = interval['startTime']
            date_obj = date.fromisoformat(date_iso[:date_iso.find('T')])
            new_weather = Weather(
                location=location,
                date=date_obj,
                temp=interval['values']['temperature'],
                weather_code=interval['values']['weatherCodeDay'],
                step='1d',
            )
            new_weather.save()
            new_weathers.append(new_weather)
        return new_weathers[0]
    elif response.status_code == 429:
        print('> Log: API request limit has been reached!')
        print('\tReturning original Weather')
    elif response.status_code == 400:
        print('> Log: API request failed due to:', response_dict['type'])
        print('\t> Response Message:', response_dict['message'])
        print('\t> Returning original Weather data:', weather)

    # if we made it here, we didn't get a new weather object. Return original one
    return weather

def add_weather_data(people: Person) -> None:
    """
    Get weather data and add as an attribute to each Person object.
    
    :param people: list of Person objects
    :side effect: adds days as an attribute to each Person object, which is a
                  list of dictionaries (keys: temp, icon, day_name) for each day
    """
    for up in people:
        location = up.person.location
        local_time_zone = pytz.timezone(location.timezone)
        local_today = datetime.now(tz=local_time_zone).date()
        local_dates = [local_today + timedelta(days=i) for i in range(3)]
        days = []
        for local_date in local_dates:
            data = {'temp': 'n/a',
                    'description': 'n/a',
                    'icon_path': None,
                    'day_name': calendar.day_name[local_date.weekday()]}
            weather = None
            try:
                query = Weather.objects.filter(location=location, date=local_date)
                # choose the weather object most recently downloaded from API
                weather = query.order_by("-timestamp")[:1].get()
            except Weather.DoesNotExist:
                pass
            finally:
                # check if Weather record pulled from database is expired
                if weather is None or weather.timestamp + API_RESULT_LIFETIME < now():
                    weather = api_request(weather, local_date, location)
            
            # update data dictionary if valid weather object was obtained
            if weather:
                data['temp'] = int(weather.temp)
                code = weather.weather_code
                data['description'] = WEATHER_CODES[str(code)]
                data['icon_path'] = get_icon_path(code)

            days.append(data)
            
        # attach days (the list of daily data dicts) to Person object
        up.person.days = days

def get_icon_path(code: str) -> Path:
    """
    Given a daily weather code, retrieve the relative path to the weather icon.

    :param str code: Tomorrow.io API weather code for a timeline of one day
    :return Path icon_path_rel: path to the icon, relative to media directory
    """
    ICONS_URL = 'static/media/images/icons/'
    ICONS_DIR = BASE_DIR.joinpath(ICONS_URL)

    icon_path_abs = next(ICONS_DIR.glob(f'{code}*.png'))
    return icon_path_abs.relative_to(BASE_DIR / 'static/media/')

# Create your views here.
# =============================================================================
def home(request):
    """Get person and weather data for display on home page"""
    context = {}
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user.username)
        people = User_Person.objects.filter(user_id=user)
        add_weather_data(people)
        context['people'] = people
    return render(request, 'weather/home.html', context)

def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('weather:home')
        else:
            context['message'] = "Invalid username or password."
    return render(request, 'weather/user_login.html', context)

def logout_request(request):
    logout(request)
    return redirect('weather:home')

def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'weather/user_registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            print(f"> Log: {username} is new user")
        if not user_exist:
            user = User.objects.create_user(username=username,
                    first_name=first_name,
                    last_name=last_name,
                    password=password)
            login(request, user)
            return redirect("weather:home")
        else:
            context['message'] = "User already exists."
            return render(request, 'weather/user_registration.html', context)
