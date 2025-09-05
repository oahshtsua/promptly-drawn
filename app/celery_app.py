from celery import Celery

from app.config import settings

celery_app = Celery(__name__)
celery_app.conf.broker_url = settings.CELERY_BROKER_URL
celery_app.autodiscover_tasks(["app.tasks"])

celery_app.conf.beat_schedule = {}
