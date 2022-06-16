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
WEATHER_CODES, WEATHER_CODES_DAY = get_codes()

# Helper functions for views
# =============================================================================
def api_request(
        weather: Weather,
        current_time: datetime,
        location: Location,
        period: str= 'day',
    ) -> Weather:
    """
    Issue an API request to obtain weather forecast for the indicated period.
    
    :param Weather weather: the current best result from the database, or None
    :param datetime current_time: current local time (tz aware)
    :param Location location: location for which weather is needed
    :param str period: 'day' for next 3 days, 'hour' for current hour
    :return: a Weather object of the successful API or request or None
    """

    TIMESTEPS = {'hour': '1h', 'day': '1d'}
    step = TIMESTEPS[period]
    TIMEDELTAS = {'hour': timedelta(hours=1), 'day': timedelta(days=3)}
    CODE_PARAM = {'hour': 'weatherCode', 'day': 'watherCodeDay'}

    local_tz = current_time.tzinfo
    lat_long = str(location.latitude) + ',' + str(location.longitude)
    params = {
        'location': lat_long,
        'startTime': current_time.isoformat(),
        'endTime': (current_time + TIMEDELTAS[period]).isoformat(),
        'timesteps': step,
        'fields': ['temperature', CODE_PARAM[period]],
        'units': 'imperial',
        'apikey': API_KEY,
    }
    response = requests.get(API_BASE_URL, params)
    response_dict = response.json()
    if response.status_code == 200:
        out_directory = BASE_DIR.parent.joinpath('mysite/weather/api-responses')
        out_filename = f"{location.name.lower().replace(' ', '-')}-" \
                       f"{current_time.date().isoformat()}-T{current_time.hour}-{step}-" \
                       f"{datetime.now().time().isoformat('seconds').replace(':','-')}.json"
        if out_directory.exists():
            with open(out_directory.joinpath(out_filename), 'w') as f:
                json.dump(response_dict, f, indent=4)
            print(' > Log: saved API response:', location.name, current_time.date(), current_time.hour, step)
        else:
            print(' > Log: API response not saved. Outfile path does not exist.')

        # now create Weather objects from API response, save, and return first
        # extract first interval (day) from response
        intervals = response_dict['data']['timelines'][0]['intervals']
        new_weathers = []
        for interval in intervals:
            time_utc = datetime.fromisoformat(interval['startTime'].replace('Z', ''))
            time_utc = time_utc.replace(tzinfo=pytz.utc)
            time_local = time_utc.astimezone(tz=local_tz)
            new_weather = Weather(
                location=location,
                date=time_local.date(),
                hour=time_local.hour,
                temp=interval['values']['temperature'],
                weather_code=interval['values'][CODE_PARAM[period]],
                step=step,
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

    Required weather data: current hour, next 3 days (starting with today)
    
    :param people: list of Person objects
    :side effect: adds days as an attribute to each Person object, which is a
                  list of dictionaries (keys: temp, icon, day_name) for each day
    """
    for up in people:
        location = up.person.location
        local_time_zone = pytz.timezone(location.timezone)
        local_now = datetime.now(tz=local_time_zone)
        local_today = local_now.date()
        local_hour = local_now.time().hour

        # --- Get current hour weather data
        weather = None
        try:
            query = Weather.objects.filter(
                location=location,
                date=local_today,
                hour=local_hour,
                step='1h')
            weather = query.order_by("-timestamp")[:1].get()
        except Weather.DoesNotExist:
            pass
        finally:
            if weather is None:
                weather = api_request(weather, local_now, location, 'hour')
        
        data = {'temp': 'n/a',
                'description': 'n/a',
                'icon_path': None,}
        if weather:
            data['temp'] = int(weather.temp)
            code = weather.weather_code
            data['description'] = WEATHER_CODES[str(code)]
            data['icon_path'] = get_icon_path(code)
        up.person.cur_weather = data

        # --- Get daily weather data
        local_dates = [local_today + timedelta(days=i) for i in range(3)]
        days = []
        for local_date in local_dates:
            data = {'temp': 'n/a',
                    'description': 'n/a',
                    'icon_path': None,
                    'day_name': calendar.day_name[local_date.weekday()]}
            weather = None
            try:
                query = Weather.objects.filter(
                    location=location,
                    date=local_date,
                    step='1d')
                weather = query.order_by("-timestamp")[:1].get()
            except Weather.DoesNotExist:
                pass
            finally:
                if weather is None or weather.timestamp + API_RESULT_LIFETIME < now():
                    weather = api_request(weather, local_now, location, 'day')
            
            # update data dictionary if valid weather object was obtained
            if weather:
                data['temp'] = int(weather.temp)
                code = weather.weather_code
                data['description'] = WEATHER_CODES_DAY[str(code)]
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
