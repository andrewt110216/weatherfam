from datetime import date

from django.db import models
from django.conf import settings
from django.utils.timezone import now # UTC timezone (per project settings)

from .funcs import get_all_timezones

TIMEZONES = get_all_timezones()

class Location(models.Model):
    name = models.CharField(max_length=30)
    latitude = models.CharField(max_length=20)
    longitude = models.CharField(max_length=20)
    TZ_NAMES = [(name, name) for name, _ in TIMEZONES.items()]
    timezone = models.CharField(max_length=30, choices=TZ_NAMES)

class Person(models.Model):
    name = models.CharField(max_length=30)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/people/',
                              default='images/person_default.jpeg')

class Weather(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=now)
    step = models.CharField(max_length=2)
    date = models.DateField(default=date(1970, 1, 1))
    hour = models.IntegerField(default=0)
    temp = models.IntegerField()
    weather_code = models.CharField(max_length=5)

class User_Person(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    date_added = models.DateField(default=now)
