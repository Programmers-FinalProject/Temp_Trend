from django.contrib import admin
from django.urls import path
import weather.views

urlpatterns = [
    path("", weather.views.mainpage, name="mainpage"),
    path("news/", weather.views.news, name="news"),
]