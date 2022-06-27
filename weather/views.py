from pathlib import Path
import requests
import json
from datetime import datetime, timedelta
import pytz

from django.shortcuts import  render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.core.files import File
from django.utils.timezone import now  # UTC timezone (per project settings)

from .models import Person, Weather, User_Person, Location
from .funcs import get_codes, get_icon_path, get_timezone

# Constants
BASE_DIR = Path(__file__).resolve().parent.parent
API_RESULT_LIFETIME = timedelta(hours=6)
WEATHER_CODES, WEATHER_CODES_DAY = get_codes()
CODES = {'hour': WEATHER_CODES, 'day': WEATHER_CODES_DAY}
CODE_PARAM = {'hour': 'weatherCode', 'day': 'weatherCodeDay'}
TIMESTEPS = {'hour': '1h', 'day': '1d'}
TIMEDELTAS = {'hour': timedelta(hours=1), 'day': timedelta(days=3)}

# VIEW FUNCTIONS
def home(request):
    context = {}
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user.username)
        user_persons = User_Person.objects.filter(user_id=user)
        for up in user_persons:
            location = up.person.location
            local_now = datetime.now(tz=pytz.timezone(location.timezone))
            data = get_weather(location, local_now, 'hour')
            up.person.cur_weather = data
            local_dates = [local_now + timedelta(days=i) for i in range(3)]
            days = []
            for local_date in local_dates:
                data = get_weather(location, local_date, 'day')
                days.append(data)
            up.person.days = days
        context['people'] = user_persons
    return render(request, 'weather/home.html', context)

def login_request(request):
    context = {}
    if request.method == "POST":
        user = authenticate(username=request.POST['username'],
                            password=request.POST['password'])
        if user:
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
        username = request.POST['username']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except User.DoesNotExist:
            pass
        if not user_exist:
            user = User.objects.create_user(username=username,
                    first_name=request.POST['firstname'],
                    last_name=request.POST['lastname'],
                    password=request.POST['password'])
            login(request, user)
            return redirect("weather:home")
        else:
            context['message'] = "User already exists."
            return render(request, 'weather/user_registration.html', context)

def add_person_request(request):
    context = {}
    if not request.user.is_authenticated:
        return render(request, 'weather/user_login.html', context)
    if request.method == 'POST':
        latitude, longitude = request.POST['lat'], request.POST['long']
        new_location = get_location(latitude, longitude, request)
        new_person = Person.objects.create(name=request.POST['name'],
                                           location=new_location)
        new_person.save()
        add_image(request, new_person)
        new_user_person = User_Person.objects.create(person=new_person,
            user=User.objects.get(username=request.user.username))
        new_user_person.save()
        return redirect("weather:home")
    return render(request, 'weather/add_person.html', context)

def update_person(request, id):
    context = {}
    if request.method == 'POST':
        person = Person.objects.get(id=id)
        latitude, longitude = request.POST['lat'], request.POST['long']
        new_location = get_location(latitude, longitude, request)
        person.name = request.POST['name']
        person.location = new_location
        person.save()
        add_image(request, person)
        return redirect("weather:home")
    return render(context, f'weather/detail-person/{id}', context)

def detail_person(request, id):
    context = {'person': Person.objects.get(id=id)}
    return render(request, 'weather/detail_person.html', context)

def delete_person(request, id):
    person_to_delete = Person.objects.get(id=id)
    person_to_delete.delete()
    return redirect("weather:home")

# HELPER FUNCTIONS
def create_weather_obj(interval: list, location: Location, period: str,
                       current_time: datetime, step: str) -> Weather:
    time_utc = datetime.fromisoformat(interval['startTime'].replace('Z', ''))
    time_utc = time_utc.replace(tzinfo=pytz.utc)
    time_local = time_utc.astimezone(tz=current_time.tzinfo)
    HOURS = {'day': 0, 'hour': time_local.hour}
    new_weather = Weather(location=location, date=time_local.date(),
        hour=HOURS[period], temp=interval['values']['temperature'],
        weather_code=interval['values'][CODE_PARAM[period]], step=step)
    new_weather.save()
    return new_weather

def save_json_response(response: dict, weather: Weather) -> None:
    out_directory = BASE_DIR.parent.joinpath('mysite/weather/api-responses')
    file_time = datetime.now().time().isoformat('seconds').replace(':','-')
    loc = weather.location.name.lower().replace(' ', '-').replace(',', '-')
    fn = f"{loc}-{weather.date}-T{weather.hour}-{weather.step}-{file_time}.json"
    if out_directory.exists():
        with open(out_directory.joinpath(fn), 'w') as f:
            json.dump(response, f, indent=4)
        print(' > Saved API response:', weather.location.name, file_time)
    else:
        print(' > API response not saved. Outfile path does not exist.')

def api_request(weather: Weather, current_time: datetime, location: Location,
                period: str) -> Weather:
    API_BASE_URL = 'https://api.tomorrow.io/v4/timelines'
    API_KEY = 'P0upWa3NF5mlabyrkmlCDqZWDblfSUUc'
    step = TIMESTEPS[period]
    coordinates = str(location.latitude) + ',' + str(location.longitude)
    params = {'location': coordinates,
              'startTime': current_time.isoformat(),
              'endTime': (current_time + TIMEDELTAS[period]).isoformat(),
              'timesteps': step,
              'fields': ['temperature', CODE_PARAM[period]],
              'units': 'imperial',
              'apikey': API_KEY,}
    response = requests.get(API_BASE_URL, params)
    response_dict = response.json()
    if response.status_code == 200:
        intervals = response_dict['data']['timelines'][0]['intervals']
        new_weathers = []
        for interval in intervals:
            new_weather = create_weather_obj(interval)
            new_weathers.append(new_weather)
            save_json_response(response_dict, new_weather)
        return new_weathers[0]
    elif response.status_code == 429:
        print('> Log: API request limit has been reached!')
    elif response.status_code == 400:
        print('> Log: API request failed due to:', response_dict['type'])
        print('\t> Response Message:', response_dict['message'])
    return weather

def query_database(location: Location, local_now: datetime, period: str):
    HOURS = {'day': 0, 'hour': local_now.time().hour}
    try:
        query = Weather.objects.filter(location=location, date=local_now.date(),
                    hour=HOURS[period],step=TIMESTEPS[period])
        return query.order_by("-timestamp")[:1].get()
    except Weather.DoesNotExist:
        return None

def get_weather(location: Location, local_now: datetime, period: str) -> dict:
    data = {'temp': 'n/a', 'description': 'n/a', 'icon_path': None}
    weather = query_database(location, local_now, period)
    if weather is None or weather.timestamp + API_RESULT_LIFETIME < now():
        weather = api_request(weather, local_now, location, period)
    if weather:
        code = weather.weather_code
        data['description'] = CODES[period][str(code)]
        data['icon_path'] = get_icon_path(code)
        data['temp'] = int(weather.temp)
        data['day_name'] = local_now.strftime("%A")
    return data

def get_location(lat: str, long: str, request) -> Location:
    try:
        new_location = Location.objects.get(latitude=lat, longitude=long)
    except Location.DoesNotExist:
        new_location = Location.objects.create(
            name=request.POST['locationName'],
            latitude=lat,
            longitude=long,
            timezone=get_timezone(lat, long))
        new_location.save()
    return new_location

def add_image(request, person):
    if request.FILES.__len__() != 0:
        person.image = File(request.FILES['formFile'])
        person.save()
