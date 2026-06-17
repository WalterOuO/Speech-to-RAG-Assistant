import os
import whisper
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.celery_app import celery
from app.db.chroma_client import get_vector_store
from app.db.status_db import update_status

vector_store = get_vector_store()
whisper_model = whisper.load_model("base")


@celery.task
def process_audio_task(audio_path: str, filename: str, transcript_path: str):
    try:
        # Whisper 轉錄
        result = whisper_model.transcribe(audio_path)
        transcript = result["text"]

        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript)
            
        # 切塊與寫入向量資料庫
        docs = [Document(page_content=transcript, metadata={"source_audio": filename})]

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=20
            )

        chunks = splitter.split_documents(docs)

        for chunk in chunks:
            chunk.metadata["source_audio"] = filename

        vector_store.add_documents(chunks)
        
        # 更新狀態
        update_status(filename, process_audio_task.request.id, "completed")

        return {
            "filename": filename,
            "status": "completed"
        }
        
    except Exception as e:
        # 失敗也更新紀錄
        update_status(filename, process_audio_task.request.id, f"failed: {str(e)}")
        raise e