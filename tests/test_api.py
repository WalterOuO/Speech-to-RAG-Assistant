import pytest
from unittest.mock import patch
from app.db.status_db import get_status

def test_api_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_api_status(client):
    res = client.get("/status")
    assert res.status_code == 200
    assert "messages" in res.json()

def test_api_rag_ask(client):
    with patch("app.api.rag.ask_question") as mock_ask:
        mock_ask.return_value = {
            "question": "test?",
            "answer": "test answer",
            "sources": []
        }
        res = client.post("/rag/ask", json={"question": "test?"})
        assert res.status_code == 200
        assert res.json()["answer"] == "test answer"

def test_api_speech_upload(client):
    with patch("app.api.speech.upload_audio") as mock_upload:
        mock_upload.return_value = {"filename": "test.wav", "status": "processing"}

        # Use a real file-like object for FastAPI
        files = {"file": ("test.wav", b"fake-audio", "audio/wav")}
        res = client.post("/speech/upload", files=files)
        assert res.status_code == 201
        assert res.json()["status"] == "processing"

def test_api_speech_status_found(client):
    with patch("app.api.speech.get_status") as mock_get:
        mock_get.return_value = {"status": "completed", "task_id": "123"}
        res = client.get("/speech/status/test.wav")
        assert res.status_code == 200
        assert res.json()["status"] == "completed"

def test_api_speech_status_404(client):
    with patch("app.api.speech.get_status") as mock_get:
        mock_get.return_value = None
        res = client.get("/speech/status/missing.wav")
        assert res.status_code == 404
        assert "not found" in res.json()["detail"]
