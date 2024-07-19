import os
import requests
from django.http import JsonResponse
from dotenv import load_dotenv
import redis
import re
from django.shortcuts import render
import urllib.parse  # urllib3 대신 urllib 사용

load_dotenv()

client_id = os.getenv("NAVER_CLIENT_ID")
client_secret = os.getenv("NAVER_CLIENT_SECRET")

# Redis 클라이언트 생성
r = redis.Redis(host='localhost', port=6379, db=0)

def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def fetch_and_store_news(request):
    if not client_id or not client_secret:
        return JsonResponse({"error": "Client ID or Client Secret not found in environment variables"}, status=500)
    
    encText = urllib.parse.quote("날씨")
    sorting = "&display=100&start=1&sort=sim"
    url = "https://openapi.naver.com/v1/search/news?query=" + encText + sorting

    headers = {
        'X-Naver-Client-Id': client_id,
        'X-Naver-Client-Secret': client_secret,
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        items = data['items']
        
        for idx, item in enumerate(items):
            item_id = f"news:{idx+1}"
            clean_title = remove_html_tags(item['title'])
            clean_description = remove_html_tags(item['description'])
            r.hset(item_id, mapping={
                "title": clean_title,
                "description": clean_description,
                "link": item['link'],
                "pubDate": item['pubDate']
            })
        
        return JsonResponse({"message": "Data successfully stored in Redis"}, status=200)
    else:
        return JsonResponse({"error": "Failed to fetch data from Naver API"}, status=response.status_code)

def display_news(request):
    keys = r.keys("news:*")
    news_items = []
    
    for key in keys:
        news_item = r.hgetall(key)
        news_items.append({
            "title": news_item[b'title'].decode('utf-8'),
            "description": news_item[b'description'].decode('utf-8'),
            "link": news_item[b'link'].decode('utf-8'),
            "pubDate": news_item[b'pubDate'].decode('utf-8')
        })
    
    return render(request, 'news.html', {"news_items": news_items})


def news_view(request):
    fetch_and_store_news(request)
    return display_news(request)
