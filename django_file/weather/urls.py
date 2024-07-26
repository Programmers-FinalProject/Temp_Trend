# weather/urls.py
from django.urls import path
from weather.view.redis import fetch_and_store_news, display_news, news_view
from weather.view.index import weather_view  # 새로 추가된 index view
from weather.tests import test

urlpatterns = [
    path('fetch-news/', fetch_and_store_news, name='fetch_news'),
    path('display-news/', display_news, name='display_news'),
    path('', weather_view, name='index'),  # 기본 경로 설정
    path('news/', news_view, name='news'),
    path('test/',test,name='test')
]