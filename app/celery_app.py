from celery import Celery, signals
from loguru import logger

from app.config import settings
from app.services.image_generation import image_gen_service

celery_app = Celery(__name__)
celery_app.conf.broker_url = settings.CELERY_BROKER_URL
celery_app.autodiscover_tasks(["app.tasks"])

celery_app.conf.beat_schedule = {}


@signals.worker_process_init.connect
def init_worker(**kwargs):
    logger.info("Initializing image generation model...")
    image_gen_service.load_model()
    logger.info("Model loaded successfully.")
