from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.contrib.auth.models import User
from datetime import date, time

# Create your models here.
class Location(models.Model):
    name = models.CharField(max_length=20)
    latitude = models.CharField(max_length=20)
    longitude = models.CharField(max_length=20)

class Person(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20, blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/people/',
                              default='images/person_default.jpeg')

class Weather(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=now)
    STEP_CHOICES = [('1d', 'Day'), ('1h', 'Hour')]
    step = models.CharField(max_length=2, choices=STEP_CHOICES)
    date = models.DateField(default=date(1970, 1, 1))
    hour = models.TimeField(default=time(0, 0))
    temp = models.IntegerField()
    feels_like = models.IntegerField()
    weather_code = models.CharField(max_length=5)

class User_Person(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    date_added = models.DateField(default=now)

    def __str__(self):
        user = User.objects.get(pk=self.user_id)
        person = Person.objects.get(pk=self.person_id)
        person_name = f'{person.first_name} {person.last_name}'.title()
        return f'User: {user.username} -> Person: {person_name}'
