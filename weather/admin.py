from django.contrib import admin
from .models import Person, Location, Weather, User_Person

# Register your models here.
admin.site.register(Person)
admin.site.register(Location)
admin.site.register(Weather)
admin.site.register(User_Person)