import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    CELERY_BROKER_URL: str
    CELERY_BACKEND_URL: str
    
    UPLOAD_AUDIO_DIR: str = "./uploaded_audio"
    TRANSCRIPT_DIR: str = "./transcripts"
    DB_PATH: str = "./file_status_db/transcripts_status.db"
    EMBEDDING_MODEL: str = "BAAI/bge-small-zh-v1.5"
    OLLAMA_MODEL: str = "llama3:latest"
    RERANKER_MODEL: str = "BAAI/bge-reranker-base"
    WHISPER_MODEL: str = "base"
    STREAMLIT_BACKEND_URL: str = "http://localhost:8002"  
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()