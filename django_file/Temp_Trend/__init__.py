from __future__ import absolute_import, unicode_literals

# 이게 Celery를 Django와 함께 사용할 수 있도록 설정함
from .celery import app as celery_app

__all__ = ('celery_app',)
