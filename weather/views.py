# Python libraries
from pathlib import Path
from datetime import date, timedelta
import calendar
# Django files
from django.shortcuts import  render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
# Local files
from .models import Person, Weather, User_Person

def get_icon_path(code):
    """
    Given a daily weather code, retrieve the relative path to the weather icon.

    :param str code: Tomorrow.io API weather code for a timeline of one day
    :return Path icon_path_rel: path to the icon, relative to media directory
    """

    BASE_DIR = Path(__file__).resolve().parent.parent
    ICONS_URL = 'static/media/images/icons/'
    ICONS_DIR = BASE_DIR.joinpath(ICONS_URL)

    icon_path_abs = next(ICONS_DIR.glob(f'{code}*.png'))
    return icon_path_abs.relative_to(BASE_DIR / 'static/media/')

def add_weather_data(people):
    """
    Get weather data and add as an attribute to each Person object.
    
    :param people: list of Person objects
    :side effect: adds days as an attribute to each Person object, which is a
                  list of dictionaries (keys: temp, icon, day_name) for each day
    """

    # Set dates for which weather data is needed
    all_dates = [date.today() + timedelta(days=i) for i in range(3)]
    
    for person in people:
        location = person.location
        days = []
        for cur_date in all_dates:
            data = {'temp': 'n/a',
                    'icon_path': None,
                    'day_name': calendar.day_name[cur_date.weekday()]}
            try:
                query = Weather.objects.filter(
                        location=location, date=cur_date, step='1d')
                # choose the weather object most recently downloaded from API
                weather = query.order_by("-timestamp")[:1].get()
            except Weather.DoesNotExist:
                print(f"> Weather not found for: {location.name}, {cur_date}")
            else:
                data['temp'] = weather.temp
                data['icon_path'] = get_icon_path(weather.weather_code)
            days.append(data)
        # attach data as attribute to person
        person.days = days

# Create your views here.
# =============================================================================
def home(request):
    """Get person and weather data for display on home page"""
    context = {}
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user.username)
        # TODO refactor this line. should be able to work with up objects, filtered on user
        # TEST - MAKING A CHANGE IN THE REFACTOR BRANCH.
        people = [Person.objects.get(pk=up.person_id) for up in user.user_person_set.all()]
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
