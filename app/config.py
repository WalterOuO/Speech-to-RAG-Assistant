import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    CELERY_BROKER_URL: str
    CELERY_BACKEND_URL: str
    
    UPLOAD_AUDIO_DIR: str = "./uploaded_audio"
    TRANSCRIPT_DIR: str = "./transcripts"
    DB_PATH: str = "./file_status_db/transcripts_status.db"
    EMBEDDING_MODEL: str = "BAAI/bge-small-zh-v1.5"
    OLLAMA_MODEL: str = "qwen2.5:1.5b"
    WHISPER_MODEL: str = "base"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()