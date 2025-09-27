import pytest
from app.worker.celery_app import celery_app


@pytest.fixture(autouse=True)
def celery_eager(monkeypatch):
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
