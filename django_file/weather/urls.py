# weather/urls.py
from django.urls import path
from weather.view.redis import fetch_and_store_news, display_news, news_view
from weather.view.index import index  # 새로 추가된 index view

urlpatterns = [
    path('fetch-news/', fetch_and_store_news, name='fetch_news'),
    path('display-news/', display_news, name='display_news'),
    path('', index, name='index'),  # 기본 경로 설정
    path('news/', news_view, name='news'),
]