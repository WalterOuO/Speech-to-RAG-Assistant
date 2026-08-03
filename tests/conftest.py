import os
import sys
import tempfile
import shutil
from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient

# 1. Setup temporary directories before any 'app' modules are imported
# This ensures that SQLite and file writes don't clutter the project root during tests
tmp_dir = tempfile.mkdtemp()
os.environ["UPLOAD_AUDIO_DIR"] = os.path.join(tmp_dir, "uploads")
os.environ["TRANSCRIPT_DIR"] = os.path.join(tmp_dir, "transcripts")
os.environ["DB_PATH"] = os.path.join(tmp_dir, "status.db")

# 2. Inject Fakes into sys.modules to prevent heavy model loading at import time
# ---------------------------------------------------------------------------

# Fake Chroma/LLM/Reranker client
fake_vector_store = MagicMock()
fake_llm = MagicMock()
fake_reranker = MagicMock()

mock_chroma_client = MagicMock()
mock_chroma_client.get_vector_store.return_value = fake_vector_store
mock_chroma_client.get_llm.return_value = fake_llm
mock_chroma_client.get_reranker.return_value = fake_reranker

sys.modules["app.db.chroma_client"] = mock_chroma_client

# Fake Whisper
mock_whisper = MagicMock()
mock_whisper_model = MagicMock()
mock_whisper.load_model.return_value = mock_whisper_model
sys.modules["whisper"] = mock_whisper

# ---------------------------------------------------------------------------

# Now we can safely import app modules
from app.main import app
from app.celery_app import celery

# 3. Configure Celery Eager Mode
# Tasks will run synchronously and return results immediately
celery.conf.task_always_eager = True
celery.conf.task_eager_propagates = True

@pytest.fixture(scope="session", autouse=True)
def cleanup_tmp_dir():
    yield
    shutil.rmtree(tmp_dir, ignore_errors=True)

@pytest.fixture
def client():
    """FastAPI TestClient fixture"""
    with TestClient(app) as c:
        yield c

@pytest.fixture
def fake_vs():
    return fake_vector_store

@pytest.fixture
def fake_llm_obj():
    return fake_llm

@pytest.fixture
def fake_rerank_obj():
    return fake_reranker
