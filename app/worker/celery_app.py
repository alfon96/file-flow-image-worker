from celery import Celery
from celery.signals import worker_init
from app.utils.context import Context
import os

broker_url = os.getenv("CELERY_BROKER_URL", "")
backend_url = os.getenv("CELERY_RESULT_BACKEND", broker_url)

celery_app = Celery("worker", broker=broker_url, backend=backend_url)
celery_app.conf.task_default_queue = "images"
celery_app.autodiscover_tasks(["app.tasks.filters", "app.tasks.scaling"])


@worker_init.connect
def init_worker(**kwargs):
    Context()
