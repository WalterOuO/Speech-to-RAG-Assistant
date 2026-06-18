import os
import shutil
from fastapi import UploadFile, HTTPException
from app.tasks.speech_tasks import process_audio_task
from app.db.status_db import update_status
from app.db.chroma_client import get_vector_store
from app.config import settings

UPLOAD_AUDIO_DIR = settings.UPLOAD_AUDIO_DIR
TRANSCRIPT_DIR = settings.TRANSCRIPT_DIR

os.makedirs(UPLOAD_AUDIO_DIR, exist_ok=True)
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)


# whisper_model = whisper.load_model("base")
vector_store = get_vector_store()

def upload_audio(file: UploadFile):
    if not (
        file.filename.endswith(".wav")
        or file.filename.endswith(".mp3")
        or file.filename.endswith(".m4a")
    ):
        raise HTTPException(
            status_code=400,
            detail="Only wav/mp3/m4a are supported."
        )

    filename = file.filename
    audio_path = os.path.join(UPLOAD_AUDIO_DIR, filename)

    existing_docs = vector_store.get(
        where={"source_audio": filename},
        limit=1
    )



    if len(existing_docs["ids"]) > 0:
        return {
            "filename": filename,
            "status": "Audio already uploaded and indexed."
        }


    with open(audio_path, "wb") as buffer:
        content = file.file.read()
        buffer.write(content)
    file.file.close()

    transcript_filename = (os.path.splitext(filename)[0] + ".txt")
    transcript_path = os.path.join(TRANSCRIPT_DIR, transcript_filename)

    # 觸發 Celery 任務
    task = process_audio_task.delay(audio_path, filename, transcript_path)

    # 紀錄進度為 "processing"
    update_status(filename, task.id, "processing")

    # 4. 回覆符合你要求的格式
    return {
        "filename": filename,
        "status": "processing"
    }

