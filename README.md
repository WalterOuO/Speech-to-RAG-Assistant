# Speech-to-RAG Assistant  
### (FastAPI + Whisper + RAG + Celery + Redis + ChromaDB + Ollama)

這是一個簡易的 **語音轉文字 + 向量檢檢索增強生成（RAG）系統**，支援音檔上傳、自動轉錄、向量化索引與語意問答，並透過 Celery 非同步處理長時間任務，具備可擴展的後端架構設計。


## 🚀 Project Overview

Speech-to-RAG Assistant 是一個端到端 AI Backend 系統，流程如下：
```text
Audio Upload
     ↓
Celery Background Task
     ↓
Whisper Model (Speech-to-Text)
     ↓
Text Chunking
     ↓
Embedding
     ↓
Chroma Vector Database
     ↓
RAG Retrieval + LLM (Ollama)
     ↓
Answer with Source Traceability
```


## 🧠 Key Features

### Speech Processing
- 支援 `.wav / .mp3 / .m4a` 音檔上傳
- 使用 OpenAI Whisper 自動語音轉文字
- 非同步背景處理（Celery + Redis）

### RAG Question Answering
- 基於 ChromaDB 向量資料庫
- 使用 HuggingFace BGE embedding
- 支援語意搜尋 + context augmentation
- 使用 Ollama (Qwen2.5) 本地推論

### Async System Design
- Celery background workers
- Redis message broker
- 任務狀態追蹤（SQLite）

### System Observability
- Audio processing status tracking
- Logging system (INFO / ERROR)
- Health check endpoint

---

## 🏗 System Architecture
```text

               ┌──────────────┐
               │ FastAPI API  │
               └──────┬───────┘
                      │
       ┌──────────────┴──────────────┐
       │                             │
  Upload Audio                   Ask Question
       │                             │
       ▼                             ▼
┌──────────────┐              ┌────────────────┐
│ Celery Task  │              │  RAG Pipeline  │
│  (Whisper)   │              │   Retrieval    │
└──────┬───────┘              └──────┬─────────┘
       │                             │
       ▼                             │
┌──────────────┐                     │
│ Transcripts  │                     │
└──────┬───────┘                     │
       │                             │
       ▼                             │
    Chunking                         ▼
       │                    ┌────────────────────┐
       ▼                    │                    │
    Embedding ─────────────►│  Chroma Vector DB  │
                            │                    │
                            └────────┬───────────┘
                                     │
                                     ▼
                             Ollama LLM (Qwen)
                                     │
                                     ▼
                                Final Answer
```

---

## 🧱 Tech Stack

### Backend
- FastAPI
- Pydantic
- Uvicorn

### AI / ML
- Whisper (Speech-to-Text)
- HuggingFace Transformers (BGE Embedding)
- Ollama (Qwen2.5 LLM)
- LangChain (Text Splitting + Vector Store)

### DataBase
- ChromaDB (Vector Database)
- SQLite (Task Status Tracking)

### Async / Queuet 
- Celery
- Redis

### DevOps
- Docker
- Docker Compose

---

## 📁 Project Structure
```text
speech-rag/
│
├── app/                            # 核心應用程式資料夾
│   ├── api/                        # API 路由控制層 (Controller)
│   │   ├── rag.py                  # 負責 RAG 問答、語意檢索的 API 端點
│   │   └── speech.py               # 負責音檔上傳、狀態查詢的 API 端點
│   │
│   ├── db/                         # 資料庫連接與初始化 (Database Layer)
│   │   ├── chroma_client.py        # ChromaDB 向量資料庫連線實例與配置
│   │   └── status_db.py            # SQLite 任務狀態資料庫初始化與讀寫連線 (配置併發安全)
│   │
│   ├── models/                     # Pydantic 資料驗證與 Schema 定義
│   │   └── schemas.py              # 定義 API 請求、回應的 Pydantic 模型
│   │
│   ├── services/                   # 核心業務邏輯層 (Service Layer)
│   │   ├── rag_service.py          # 封裝 LangChain、檢索增強與 LLM 生成邏輯
│   │   └── speech_service.py       # 處理檔案儲存與調用 Celery 背景任務邏輯
│   │
│   ├── tasks/                      # Celery 背景非同步任務定義
│   │   └── speech_tasks.py         # 實作 Whisper 語音轉文字、文字切片與向量化儲存任務
│   │
│   ├── config.py                   # 環境配置管理
│   ├── celery_app.py               # Celery 核心實例配置 (內建 Python 動態任務自動掃描註冊機制)
│   └── main.py                     # FastAPI 進入點 (內建 Lifespan 延遲引入機制，優化開機下載模型體驗)
│
├── uploaded_audio/                 # [Bind Mount] 本機音檔上傳暫存目錄
├── transcripts/                    # [Bind Mount] 本機轉錄純文字檔預留目錄
├── file_status_db/                 # [Bind Mount] 本機 SQLite 資料庫儲存目錄 (transcripts_status.db)
├── chroma_langchain_db/            # [Bind Mount] 本機 ChromaDB 向量資料庫持久化目錄
│
├── Dockerfile                      # 用於打包 FastAPI 與 Celery Worker 的多功能環境映像檔定義
├── docker-compose.yml              # 系統多容器編排設定檔 (Web, Worker, Redis, 外部共用 Ollama 通道)
├── requirements.txt                # 專案 Python 套件依賴清單
└── .env.example                    # 環境變數範例檔
```

---

## 🔌 API Documentation

### Upload Audio

```http
POST /speech/upload
```

Request:
```text
form-data:
file: audio file (.wav, .mp3, .m4a)
```

Response:
```json
{
  "filename": "meeting.wav",
  "status": "processing"
}
```

### Check Processing Status

```http
GET /speech/status/{filename}
```

Response:
```json
{
  "filename": "meeting.wav",
  "status": "completed"
}
```

### Ask Question (RAG)
```http
POST /rag/ask
```

Request:
```json
{
  "filename": "meeting.wav",
  "question": "What is the main topic discussed?"
}
```

Response:
```json
{
  "filename": "meeting.wav",
  "question": "What is the main topic discussed?",
  "answer": "The main topic is ...",
  "sources": [
    {
      "filename": "meeting.wav",
      "chunk": 1
    },
    {
      "filename": "meeting.wav",
      "chunk": 2
    }
  ]
}
```

---

## ⚙️ Environment Variables

本專案透過 app/config.py 的 Pydantic 進行環境變數檢驗。請複製 .env.example 並重新命名為 .env，設定以下變數：
```code
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_BACKEND_URL=redis://redis:6379/0
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=YOUR_LANGSMITH_API_KEY
```


## 🐳 Run with Docker

```bash
docker-compose up -d --build
```
服務分配：
- FastAPI Backend: http://localhost:8002
- Redis: 內部消息佇列服務（Port: 6379）
- Celery Worker: 背景音訊非同步處理行程
- Ollama (LLM): 透過 host.docker.internal 通道安全串接本地既有 Ollama，共享模型記憶體。



## 🔄 Celery Workflow
```text
Upload Audio
      ↓
FastAPI stores file
      ↓
Celery task triggered
      ↓
Whisper transcription
      ↓
Chunking + Embedding
      ↓
Store into ChromaDB
      ↓
Update SQLite status
```

---

## 📌 Highlights

- 完整端到端 AI 系統：成功整合語音轉文字（STT）與檢索增強生成（RAG）兩大核心 Pipeline。
- 非同步高效能架構：採用 FastAPI + Celery + Redis 生態系，將密集型運算（Whisper / Embedding）與 API 主行程解耦。
- 高維護性設定管理：導入 Pydantic BaseSettings 實作動態 Config 機制，具備 Windows 跨平台編碼相容性。
- 極致化硬體優化：透過 Docker 進階網路配置實作容器與宿主機 Ollama 共用，節省 3.5G 記憶體開銷。
- 系統強健性設計：
    - 導入 FastAPI lifespan 延遲引入機制，確保模型與向量庫加載時的流量控制。
    - 實作 SQLite timeout 併發鎖定機制，解決多容器 Process 同時寫入的數據併發衝突。
    - 實作 Python 動態檔案系統掃描技術，解決 Celery 自動註冊任務時的常規路徑問題。
- 來源可追溯性：LLM 回應內容均附帶原始資料區塊來源，具備商業落地價值。


## 🚀 Future Improvements
- 增加多用戶身分驗證與權限控管 (JWT / OAuth2)
- 將輕量型 SQLite 升級為生產環境級的 PostgreSQL 資料庫
- 打造前端互動式儀表板介面 (React / Next.js)
- 支援音檔線上預覽與音訊波形視覺化 UI
- 擴充多語系轉錄優化與跨語言問答對齊機制