import pytest
from fastapi import HTTPException, UploadFile
from unittest.mock import patch, MagicMock
from app.services import speech_service

class FakeUploadFile:
    def __init__(self, filename, content):
        self.filename = filename
        self.file = MagicMock()
        self.file.read.return_value = content
        self.file.close = MagicMock()

def test_upload_audio_bad_extension():
    file = FakeUploadFile("test.txt", b"content")
    with pytest.raises(HTTPException) as exc:
        speech_service.upload_audio(file)
    assert exc.value.status_code == 400
    assert "Only wav/mp3/m4a are supported" in exc.value.detail

def test_upload_audio_dedup():
    file = FakeUploadFile("test.wav", b"content")
    with patch("app.services.speech_service.vector_store") as mock_vs:
        # Mock existing document
        mock_vs.get.return_value = {"ids": ["some_id"]}
        res = speech_service.upload_audio(file)
        assert res["status"] == "Audio already uploaded and indexed."

def test_upload_audio_success():
    file = FakeUploadFile("new.wav", b"audio-data")
    with patch("app.services.speech_service.vector_store") as mock_vs, \
         patch("app.services.speech_service.process_audio_task") as mock_task, \
         patch("app.services.speech_service.update_status") as mock_status:

        mock_vs.get.return_value = {"ids": []}
        mock_task.delay.return_value = MagicMock(id="task_abc")

        res = speech_service.upload_audio(file)
        assert res["status"] == "processing"
        assert res["filename"] == "new.wav"
        mock_task.delay.assert_called_once()
        mock_status.assert_called_once_with("new.wav", "task_abc", "processing")
