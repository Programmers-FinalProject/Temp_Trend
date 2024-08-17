import threading
from django.shortcuts import render
import redis
from weather.models import News
import sched
import time
from datetime import datetime, timedelta

# 스케줄러 생성
scheduler = sched.scheduler(time.time, time.sleep)

def schedule_tasks():
    now = datetime.now()
    next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    delay_until_next_hour = (next_hour - now).total_seconds()

    # 첫 번째 실행 시간을 설정 (정각)
    first_run_time = time.time() + delay_until_next_hour

    # 1분 간격으로 5번 작업을 예약
    for i in range(5):
        scheduler.enterabs(first_run_time + i * 60, 1, store_to_redis())

    # 스케줄러 시작
    scheduler.run()

# Redis 클라이언트 생성
r = redis.Redis(host='localhost', port=6379, db=0)


def store_to_redis():
    newslists = News.objects.using('redshift').all().values()
    for news in newslists:
        r.hmset( news["id"], news)
    return print("뉴스 업데이트 완료")

def display_news(request):
    keys = r.keys("news:*")
    news_items = []
    for key in keys:
        
        news_item = r.hgetall(key)
        news_items.append({
            "title": news_item[b'title'].decode('utf-8'),
            "description": news_item[b'description'].decode('utf-8'),
            "link": news_item[b'link'].decode('utf-8'),
            "pubDate": news_item[b'pubDate'].decode('utf-8'),
            "image_url": news_item[b'image_url'].decode('utf-8') if b'image_url' in news_item else None
        })
    
    context = {
        'news_items': news_items,
    }
    
    return render(request, 'news.html', context)

def news_view(request):
    thread = threading.Thread(target=schedule_tasks)
    thread = threading.Thread(target=store_to_redis)
    thread.start()
    print("thread.start()")
    store_to_redis()
    return display_news(request)

