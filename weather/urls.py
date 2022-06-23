from django.urls import path

from . import views

app_name = 'weather'
urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name='logout'),
    path('registration/', views.registration_request, name='registration'),
    path('add-person/', views.add_person_request, name='add-person'),
    path('detail-person/<int:id>/', views.detail_person, name='detail-person'),
    path('delete-person/<int:id>/', views.delete_person, name='delete-person'),
    path('update-person/<int:id>/', views.update_person, name='update-person'),
]