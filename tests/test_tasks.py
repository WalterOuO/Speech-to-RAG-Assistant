import pytest
from unittest.mock import patch, mock_open
from app.tasks import speech_tasks

def test_process_audio_task_success():
    # 測試輸入條件
    audio_path = "test.wav"
    filename = "test.wav"
    transcript_path = "test.txt"
    fake_transcript_text = "This is a test transcript for Whisper."

    # 建立檔案寫入 Mock
    m_open = mock_open()

    with patch("app.tasks.speech_tasks.whisper_model") as mock_whisper, \
         patch("app.tasks.speech_tasks.vector_store") as mock_vs, \
         patch("app.tasks.speech_tasks.update_status") as mock_status, \
         patch("builtins.open", m_open):

        # 設定 Whisper 的假回傳
        mock_whisper.transcribe.return_value = {"text": fake_transcript_text}

        # 推進 Celery Request Context
        speech_tasks.process_audio_task.push_request(id="task_123")
        try:
            res = speech_tasks.process_audio_task(audio_path, filename, transcript_path)
        finally:
            speech_tasks.process_audio_task.pop_request()

        # 1. 驗證最終回傳值
        assert res == {"filename": "test.wav", "status": "completed"}

        # 2. 驗證 Whisper 是否真的用我們傳進去的 audio_path 被呼叫
        mock_whisper.transcribe.assert_called_once_with("test.wav")

        # 3. 驗證 open() 是否開了正確的檔案，且 write() 寫入了 Whisper 的轉錄結果
        m_open.assert_called_once_with("test.txt", "w", encoding="utf-8")
        m_open().write.assert_called_once_with(fake_transcript_text)

        # 4. 驗證向量資料庫（VectorStore）接收到的 Documents 內容與 Metadata
        mock_vs.add_documents.assert_called_once()
        
        # 抓出實際被傳進 add_documents() 的 chunks 參數
        added_chunks = mock_vs.add_documents.call_args[0][0]
        assert len(added_chunks) > 0
        assert added_chunks[0].page_content == fake_transcript_text
        assert added_chunks[0].metadata["source_audio"] == "test.wav"

        # 5. 驗證 SQLite 狀態更新傳送的參數
        mock_status.assert_called_once_with("test.wav", "task_123", "completed")


def test_process_audio_task_failure():
    audio_path = "test.wav"
    filename = "test.wav"
    transcript_path = "test.txt"

    with patch("app.tasks.speech_tasks.whisper_model") as mock_whisper, \
         patch("app.tasks.speech_tasks.update_status") as mock_status:

        # 模擬 Whisper 拋出例外
        mock_whisper.transcribe.side_effect = RuntimeError("Whisper CUDA OOM")

        speech_tasks.process_audio_task.push_request(id="task_err_999")
        try:
            with pytest.raises(RuntimeError) as exc:
                speech_tasks.process_audio_task(audio_path, filename, transcript_path)
        finally:
            speech_tasks.process_audio_task.pop_request()

        # 驗證錯誤訊息有被拋出
        assert "Whisper CUDA OOM" in str(exc.value)

        # 驗證即使失敗，是否有把錯誤原因寫入資料庫
        mock_status.assert_called_once_with("test.wav", "task_err_999", "failed: Whisper CUDA OOM")