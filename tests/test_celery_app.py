import pytest
from app.celery_app import celery

def test_celery_config():
    assert celery.main.name == "speech_tasks"
    # Check if tasks are registered (should include speech_tasks)
    registered_tasks = celery.tasks.keys()
    assert any("speech_tasks" in t or "process_audio_task" in t for t in registered_tasks)

def test_celery_eager_mode():
    # In conftest.py we set task_always_eager = True
    assert celery.conf.task_always_eager is True
