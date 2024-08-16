import redis

# Redis 클라이언트 생성
r = redis.Redis(host='34.64.100.195', port=6379, db=1)
item_id = f"news:{idx+1}"

keys = r.keys("news:*")
print("Keys:", keys)

'''# 각 키의 값 조회
for key in keys:
    value = r.get(key)
    print(f"Key: {key}, Value: {value}")

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
client_secret = os.getenv("NAVER_CLIENT_SECRET")'''