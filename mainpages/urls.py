from django.urls import path
from . import views


urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('auth', views.auth_page, name='auth'),
    path('auth/login', views.login_page, name='login'),
    path('auth/registration', views.registration_page, name='registration'),
    path('logout_user', views.logout_user, name='logout_user'),
    path('road_map', views.road_map, name='road_map'),
]