<<<<<<< Updated upstream
from django.apps import AppConfig


class WeatherConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'weather'
=======
from django.apps import AppConfig
from django.db.models.signals import post_migrate

def setup_periodic_tasks(sender, **kwargs):
    from celery.schedules import crontab
    from django_celery_beat.models import PeriodicTask, CrontabSchedule
    from weather.tasks import update_news

    schedule, created = CrontabSchedule.objects.get_or_create(
        minute='*/30',  # 30분마다 실행
        hour='*',
        day_of_week='*',
        day_of_month='*',
        month_of_year='*',
    )

    PeriodicTask.objects.get_or_create(
        crontab=schedule,
        name='update news every 30 minutes',
        task='weather.tasks.update_news',
    )

class WeatherAppConfig(AppConfig):
    name = 'weather'

    def ready(self):
        post_migrate.connect(setup_periodic_tasks, sender=self)
>>>>>>> Stashed changes
