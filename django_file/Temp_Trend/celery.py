from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Django의 기본 settings 모듈을 Celery의 설정으로 사용하도록 지정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Temp_Trend.settings')

app = Celery('Temp_Trend')

# 문자열로 설정하므로, worker가 자식 프로세스로 설정 객체를 직렬화하지 않아도 됨
app.config_from_object('django.conf:settings', namespace='CELERY')

# Django의 모든 앱에서 task 모듈을 불러옴
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
