# weather/urls.py
from django.urls import path
from weather.view.redis import fetch_and_store_news, display_news, news_view
from weather.view.index import weather_view  # 새로 추가된 index view
from weather.view import weather_views
from weather.view.musinsa_views import musinsa_list
from weather.view.musinsa_views import categorize
from weather.tests import test
from weather.view.save_location import save_location,location_name,session_data_api
from weather.view.cookie import show_cookies

urlpatterns = [
    # 기본 경로 설정
    path('', weather_view, name='index'),
    #뉴스페이지
    path('news/', news_view, name='news'), 
    path('fetch-news/', fetch_and_store_news, name='fetch_news'),
    path('display-news/', display_news, name='display_news'),
    #위치 저장, 위치 정보 보여주기 endpoint
    path('save_location/', save_location, name='save_location'),
<<<<<<< HEAD
    path('musinsa-test/', musinsa_list, name='musinsa_list'),
    path('categorize/', categorize, name='categorize'),
=======
    path('location_name/', location_name, name='location_name'),
    path('api/session-address/', session_data_api, name='get_session_address'),
    #테스트페이지
    path('test/',test,name='test'),
    path('musinsa-test/', musinsa_list, name='musinsa_list'), #무신사 테스트페이지
    path('we-data-test/', weather_views.we_data_test, name='wedatatest'),
    path('show_cookie', show_cookies ,name='show_cookies'), #쿠키테스트   
>>>>>>> develop
]