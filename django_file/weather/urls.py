# weather/urls.py
from django.urls import path
from weather.view.redis import fetch_and_store_news, display_news, news_view
from weather.view.index import weather_view  # 새로 추가된 index view
from weather.view import weather_views
from weather.tests import test
from weather.view.save_location import save_location

urlpatterns = [
    path('fetch-news/', fetch_and_store_news, name='fetch_news'),
    path('display-news/', display_news, name='display_news'),
    path('', weather_view, name='index'),  # 기본 경로 설정
    path('news/', news_view, name='news'),
    path('test/',test,name='test'),
    path('we-data-test/', weather_views.we_data_test, name='wedatatest'),
    path('save_location/', save_location, name='save_location'),
]