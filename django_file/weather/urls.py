# weather/urls.py
from django.urls import path
from weather.view.redis import fetch_and_store_news, display_news, news_view
<<<<<<< Updated upstream
from weather.view.index import index  # 새로 추가된 index view
=======
from weather.view.index import weather_view  # 새로 추가된 index view
from weather.tests import test
>>>>>>> Stashed changes

urlpatterns = [
    path('fetch-news/', fetch_and_store_news, name='fetch_news'),
    path('display-news/', display_news, name='display_news'),
    path('', index, name='index'),  # 기본 경로 설정
    path('news/', news_view, name='news'),
<<<<<<< Updated upstream
]
=======
    path('test/',test,name='test'),
    ]
>>>>>>> Stashed changes
