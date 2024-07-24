from celery import shared_task
from weather.view.redis import fetch_and_store_news

@shared_task
def update_news():
    fetch_and_store_news(None)  # request 객체는 필요하지 않으므로 None 전달