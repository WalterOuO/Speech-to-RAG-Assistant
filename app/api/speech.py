from fastapi import APIRouter, UploadFile, File, status
from app.models.schemas import AudioUploadResponse, AudioStatusResponse
from app.services.speech_service import upload_audio
from app.db.status_db import get_status


router = APIRouter(
    prefix="/speech",
    tags=["Speech"]
)


@router.post("/upload", response_model=AudioUploadResponse, status_code=status.HTTP_201_CREATED)
def audio_upload(file: UploadFile = File(...)):
    return upload_audio(file)


@router.get("/status/{filename}", response_model=AudioStatusResponse)
def get_audio_status(filename: str):
    record = get_status(filename)
    
    if not record:
        raise HTTPException(status_code=404, detail="Audio file task not found.")
        
    return {
        "filename": filename,
        "status": record["status"]
    }