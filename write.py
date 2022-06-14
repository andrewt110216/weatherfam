"""Write test data to the database"""
from pathlib import Path
import os
# Django specific settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
from django.db import connection
# Ensure settings are read
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from weather.models import *
from datetime import date, time, datetime, timezone
from django.contrib.auth import get_user_model
from django.core.files import File

def decorator(func):
    def wrapper():
        print('> Writing data with', func.__name__)
        func()
        print('> Saved data written by', func.__name__)
    return wrapper

@decorator
def write_location():
    location1 = Location(
        name='Santa Monica',
        latitude='34.01927618420224',
        longitude='-118.49376589583301',
    )
    location1.save()
    location2 = Location(
        name='Chicago',
        latitude='41.9251221810808',
        longitude='-87.63741632179469',
    )
    location2.save()

@decorator
def write_person():
    andrew = Person(
        first_name='Andrew',
        last_name='Tracey',
        location=Location.objects.get(name='Santa Monica'),
    )
    andrew.save()
    imgpath = Path('/Users/atracey/Pictures/headshots/at-headshot-wedding-greenery.jpeg')
    with open(imgpath, 'rb') as f:
        andrew.image = File(f, name=imgpath.name)
        andrew.save()

    lisa = Person(
        first_name='Lisa',
        last_name='Grigaliunas',
        location=Location.objects.get(name='Santa Monica'),
    )
    lisa.save()
    imgpath = Path('/Users/atracey/Pictures/headshots/lg-headshot-wedding-greenery.jpeg')
    with open(imgpath, 'rb') as f:
        lisa.image = File(f, name=imgpath.name)
        lisa.save()

    ben = Person(
        first_name='Ben',
        last_name='Tracey',
        location=Location.objects.get(name='Chicago'),
    )
    ben.save()
    imgpath = Path('/Users/atracey/Pictures/headshots/bt-headshot-wedding-river.png')
    with open(imgpath, 'rb') as f:
        ben.image = File(f, name=imgpath.name)
        ben.save()

@decorator
def write_weather():
    # SANTA MONICA WEATHER - 4 DAYS
    day1 = Weather(
        location=Location.objects.get(name='Santa Monica'),
        timestamp=datetime(2022, 6, 9, 10, 0, tzinfo=timezone.utc),
        date = date(2022, 6, 9),
        step = '1d',
        temp=68,
        feels_like=68,
        weather_code=21080,
    )
    day1.save()
    day2 = Weather(
        location=Location.objects.get(name='Santa Monica'),
        timestamp=datetime(2022, 6, 9, 10, 0, tzinfo=timezone.utc),
        date = date(2022, 6, 10),
        step = '1d',
        temp=71,
        feels_like=71,
        weather_code=21060,
    )
    day2.save()
    day3 = Weather(
        location=Location.objects.get(name='Santa Monica'),
        timestamp=datetime(2022, 6, 9, 10, 0, tzinfo=timezone.utc),
        date = date(2022, 6, 11),
        step = '1d',
        temp=72,
        feels_like=72,
        weather_code=10000,
    )
    day3.save()
    day4 = Weather(
        location=Location.objects.get(name='Santa Monica'),
        timestamp=datetime(2022, 6, 9, 10, 0, tzinfo=timezone.utc),
        date = date(2022, 6, 12),
        step = '1d',
        temp=74,
        feels_like=74,
        weather_code=10000,
    )
    day4.save()

    # CHICAGO WEATHER - 4 DAYS
    day1 = Weather(
        location=Location.objects.get(name='Chicago'),
        timestamp=datetime(2022, 6, 9, 10, 0, tzinfo=timezone.utc),
        date = date(2022, 6, 9),
        step = '1d',
        temp=69,
        feels_like=69,
        weather_code=10000,
    )
    day1.save()
    day2 = Weather(
        location=Location.objects.get(name='Chicago'),
        timestamp=datetime(2022, 6, 9, 10, 0, tzinfo=timezone.utc),
        date = date(2022, 6, 10),
        step = '1d',
        temp=77,
        feels_like=77,
        weather_code=10010,
    )
    day2.save()
    day3 = Weather(
        location=Location.objects.get(name='Chicago'),
        timestamp=datetime(2022, 6, 9, 10, 0, tzinfo=timezone.utc),
        date = date(2022, 6, 11),
        step = '1d',
        temp=73,
        feels_like=73,
        weather_code=10010,
    )
    day3.save()
    day4 = Weather(
        location=Location.objects.get(name='Chicago'),
        timestamp=datetime(2022, 6, 9, 10, 0, tzinfo=timezone.utc),
        date = date(2022, 6, 12),
        step = '1d',
        temp=66,
        feels_like=66,
        weather_code=21000,
    )
    day4.save()

@decorator
def write_user_person():
    UserModel = get_user_model()
    user_admin = UserModel.objects.get(username='admin')

    person_andrew = Person.objects.get(first_name="Andrew")
    admin_andrew = User_Person(user=user_admin, person=person_andrew)
    admin_andrew.save()

    person_lisa = Person.objects.get(first_name="Lisa")
    admin_lisa = User_Person(user=user_admin, person=person_lisa)
    admin_lisa.save()

    person_ben = Person.objects.get(first_name="Ben")
    admin_ben = User_Person(user=user_admin, person=person_ben)
    admin_ben.save()

def clean_data():
    print('> Cleaning database')
    Person.objects.all().delete()
    Location.objects.all().delete()
    Weather.objects.all().delete()
    User_Person.objects.all().delete()
    print('> Database cleaned.')

# DRIVER CODE
clean_data()
write_location()
write_person()
write_weather()
write_user_person()
