import os
import requests
from django.http import JsonResponse
from dotenv import load_dotenv
import redis
import re
from django.shortcuts import render
import urllib.parse
import html
from bs4 import BeautifulSoup
from weather.models import LocationRecord


def decode_html_entities(text):
    return html.unescape(text)

load_dotenv()

client_id = os.getenv("NAVER_CLIENT_ID")
client_secret = os.getenv("NAVER_CLIENT_SECRET")

# Redis 클라이언트 생성
r = redis.Redis(host='localhost', port=6379, db=0)

def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def get_image_from_url(news_url):
    try:
        html_content = requests.get(news_url).text
        soup = BeautifulSoup(html_content, "html.parser")
        meta_og_image = soup.find("meta", property="og:image")
        if meta_og_image:
            return meta_og_image["content"]
        else:
            return "not found -> meta tag og:image"
    except Exception as e:
        print(f"get_meta_og_image | error: {e}")
        return None

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
            clean_title = decode_html_entities(remove_html_tags(item['title']))
            clean_description = decode_html_entities(remove_html_tags(item['description']))
            image_url = get_image_from_url(item['link'])  # 이미지 URL 크롤링
            r.hset(item_id, mapping={
                "title": clean_title,
                "description": clean_description,
                "link": item['link'],
                "pubDate": item['pubDate'],
                "image_url": image_url if image_url else ""
            })
        
        return JsonResponse({"message": "Data successfully stored in Redis"}, status=200)
    else:
        return JsonResponse({"error": "Failed to fetch data from Naver API"}, status=response.status_code)

def display_news(request):
    latest_location = LocationRecord.objects.order_by('-created_at').first()
    
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
        'latest_location': latest_location,
        'news_items': news_items,

    }
    
    return render(request, 'news.html', context)

def news_view(request):
    #fetch_and_store_news(request)
    return display_news(request)
