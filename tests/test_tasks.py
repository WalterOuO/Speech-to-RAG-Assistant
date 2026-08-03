import pytest
from unittest.mock import patch, MagicMock
from app.tasks import speech_tasks

def test_process_audio_task_success():
    # Mock inputs
    audio_path = "test.wav"
    filename = "test.wav"
    transcript_path = "test.txt"

    # Mock Whisper and Vector Store
    with patch("app.tasks.speech_tasks.whisper_model") as mock_whisper, \
         patch("app.tasks.speech_tasks.vector_store") as mock_vs, \
         patch("app.tasks.speech_tasks.update_status") as mock_status:

        mock_whisper.transcribe.return_value = {"text": "This is a test transcript."}

        # We must mock process_audio_task.request.id because the task reads it
        with patch("app.tasks.speech_tasks.process_audio_task") as mock_task_obj:
            mock_task_obj.request = MagicMock(id="task_123")
            # Call the actual function logic (unwrapped from decorator)
            res = speech_tasks.process_audio_task(audio_path, filename, transcript_path)

            assert res["status"] == "completed"
            mock_vs.add_documents.assert_called_once()
            mock_status.assert_called_once_with(filename, "task_123", "completed")

def test_process_audio_task_failure():
    audio_path = "test.wav"
    filename = "test.wav"
    transcript_path = "test.txt"

    with patch("app.tasks.speech_tasks.whisper_model") as mock_whisper, \
         patch("app.tasks.speech_tasks.update_status") as mock_status:

        mock_whisper.transcribe.side_effect = Exception("Whisper Error")

        with patch("app.tasks.speech_tasks.process_audio_task") as mock_task_obj:
            mock_task_obj.request = MagicMock(id="task_err")
            with pytest.raises(Exception) as exc:
                speech_tasks.process_audio_task(audio_path, filename, transcript_path)
            assert "Whisper Error" in str(exc.value)
            mock_status.assert_called_once_with(filename, "task_err", "failed: Whisper Error")
