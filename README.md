# Speech-to-RAG Assistant

An end-to-end AI pipeline that transforms spoken audio into a searchable knowledge base with grounded, traceable Q&A capabilities.

## 🚀 Project Overview

The **Speech-to-RAG Assistant** is a high-production grade backend system designed to handle the full lifecycle of audio-based knowledge extraction: from raw audio upload to a high-precision Retrieval-Augmented Generation (RAG) interface.

### High-Level Data Flow
```text
[Audio Upload] 
       ↓
[Celery Background Task] → [OpenAI Whisper] → [Text Transcription]
       ↓
[Recursive Text Chunking] → [BGE Embedding] → [Chroma Vector DB]
       ↓
[User Query] → [Hybrid Search] → [CrossEncoder Reranking] → [Ollama LLM]
       ↓
[Grounded Answer with Source Traceability]
```

---

## 🏗️ System Architecture

The system is orchestrated via Docker Compose, utilizing a decoupled, event-driven architecture to ensure that computationally expensive AI tasks do not block the API responsiveness.

### Infrastructure Diagram
```text
                         ┌───────────────────────┐
                         │  Streamlit Frontend   │
                         │        :8501          │
                         └───────────┬───────────┘
                                     │ 
                                     │  HTTP REST
                                     ▼
                         ┌───────────────────────┐
                         │   FastAPI Backend     │
                         │        :8002          │
                         └───────────┬───────────┘
                                     │
                      ┌──────────────┴──────────────┐
                      │                             │
                      ▼                             ▼
             ┌─────────────────┐          ┌──────────────────┐
             │ Upload Pipeline │          │   RAG Pipeline   │
             └────────┬────────┘          └────────┬─────────┘
                      │                            │
                      ▼                            ▼
               ┌─────────────┐            ┌─────────────────┐
               │ Redis Broker│            │  Hybrid Search  │
               └──────┬──────┘            │  (Dense + BM25) │
                      │                   └────────┬────────┘
                      ▼                            ▼
               ┌─────────────┐            ┌─────────────────┐
               │ CeleryWorker│            │    Reranker     │
               │   Whispe    │            └────────┬────────┘
               │  Embedding  │                     │
               └──────┬──────┘                     ▼
                      │                   ┌─────────────────┐
                      ▼                   │   Ollama LLM    │
               ┌─────────────┐            └─────────────────┘
               │  Vector DB  │
               │   Chroma    │
               └─────────────┘


               SQLite Status DB
            (Task Status Tracking)
```

### The RAG Pipeline: Engineering Depth
To solve the "lost in the middle" problem and ensure high precision, the system implements a multi-stage retrieval strategy:

1.  **Hybrid Search (Ensemble Retrieval):**
    *   **Dense Vector Search:** Captures semantic meaning using `BAAI/bge-small-zh-v1.5`.
    *   **BM25 Keyword Search:** Ensures exact term matching for technical jargon or specific names.
    *   **Fusion:** Combines both using an `EnsembleRetriever` with a 50/50 weight distribution, retrieving the top 20 candidates.
2.  **Cross-Encoder Reranking:**
    *   The top 20 candidates are passed through a `CrossEncoder` (`BAAI/bge-reranker-base`).
    *   Unlike bi-encoders (vector search), the Cross-Encoder performs full-attention interaction between the query and each document, providing far more accurate relevance scores.
    *   **Final Selection:** Only the top 5 reranked documents are passed to the LLM.
3.  **Grounded Generation:**
    *   A strict system prompt forces the LLM to answer **only** based on the provided context.
    *   **Fallback:** If context is insufficient, the system returns a standardized "No answer found in document" message instead of hallucinating.

---

## ✨ Key Features

### 🎙️ Speech Processing Pipeline
*   **Asynchronous Processing:** Audio files (`.wav`, `.mp3`, `.m4a`) are processed in the background via Celery to prevent API timeouts.
*   **Automatic Transcription:** Uses OpenAI Whisper for robust speech-to-text conversion.
*   **Dynamic State Tracking:** Real-time task status (processing $\rightarrow$ completed/failed) is persisted in SQLite.

### 🔍 Advanced RAG Interface
*   **Source Traceability:** Every answer is linked to specific chunks and original filenames, allowing users to verify LLM claims.
*   **Optimized Context Window:** Reranking ensures the LLM receives only the most relevant information, reducing noise and cost.

### 💻 Interactive Frontend
*   **Streamlit Dashboard:** A clean UI for file uploads, status monitoring, and an interactive chat interface.
*   **Smart Filename Resolution:** Automatically handles extension matching (e.g., searching for "meeting" will check "meeting.wav", "meeting.mp3", etc.).
*   **System Health Polling:** Frontend polls the `/status` endpoint to ensure the backend is fully loaded before allowing interaction.

---

## 🛠️ Tech Stack

| Layer | Technology | Usage |
| :--- | :--- | :--- |
| **Backend** | FastAPI, Pydantic | High-performance REST API & data validation |
| **Async** | Celery, Redis | Distributed task queue for AI workloads |
| **AI/ML** | Whisper, BGE Embedding, CrossEncoder | STT, Vectorization, and Reranking |
| **LLM** | Ollama (Llama 3) | Local LLM inference |
| **Vector DB** | ChromaDB | Persistent vector storage and similarity search |
| **Database** | SQLite | Task status tracking |
| **Frontend** | Streamlit | Interactive User Interface |
| **DevOps** | Docker, GitHub Actions | Containerization & CI/CD Pipeline |

---

## 🧪 Quality Assurance & CI/CD

The project follows rigorous software engineering practices to ensure stability.

### Test Suite
*   **Comprehensive Coverage:** 31+ tests across 12 modules covering API endpoints, RAG logic, Celery tasks, and Config.
*   **Advanced Mocking Strategy:** In `tests/conftest.py`, heavy AI models (Whisper, Chroma, LLM) are replaced with `MagicMock` during testing to ensure the suite runs in seconds without requiring a GPU.
*   **Eager Execution:** Celery is configured in `task_always_eager` mode for tests, allowing asynchronous tasks to be tested synchronously.
*   **Run Tests:** `pytest tests/ --cov=app`

### CI/CD Pipeline
Integrated via **GitHub Actions** (`.github/workflows/cicd.yml`):
1.  **Build & Test:** Automatically triggers on push/PR. Spins up a Redis container, runs static analysis (`compileall`), and executes the full test suite with coverage reports.
2.  **Docker Build:** Uses Docker Buildx to verify that the production image builds successfully.
3.  **CD Template:** Ready for deployment via SSH or CD agents upon merging to `main`.

---

## 📁 Project Structure

```text
speech-rag/
├── .github/workflows/    # CI/CD Pipeline definitions
├── app/
│   ├── api/              # API Layer (RAG & Speech endpoints)
│   ├── db/               # Database Clients (Chroma & SQLite)
│   ├── models/           # Pydantic Schemas
│   ├── services/         # Core Business Logic (RAG, Speech, Prompts)
│   ├── tasks/            # Celery Background Tasks
│   ├── config.py         # Pydantic BaseSettings (Env management)
│   ├── celery_app.py     # Celery Configuration (Dynamic task discovery)
│   └── main.py           # FastAPI Entry point (with Lifespan management)
├── tests/                # Comprehensive Test Suite
├── frontend.py           # Streamlit Interactive UI
├── Dockerfile            # Multi-purpose AI environment image
└── docker-compose.yml    # 5-Service Orchestration (Web, Worker, Redis, Frontend, Ollama)
```

---

## ⚙️ Installation & Setup

### Environment Variables
Create a `.env` file based on `.env.example`:
```env
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_BACKEND_URL=redis://redis:6379/0
OLLAMA_HOST=http://host.docker.internal:11434
HF_TOKEN=your_huggingface_token
STREAMLIT_BACKEND_URL=http://web:8002
```

### Run with Docker
```bash
docker-compose up -d --build
```

**Service Ports:**
*   **Frontend:** `http://localhost:8501`
*   **Backend API:** `http://localhost:8002`

---

## 🌟 Engineering Highlights (Interview Points)

*   **Resource Optimization:** Implemented `host.docker.internal` networking to share a single Ollama instance across containers, saving ~3.5GB of VRAM.
*   **Concurrency Handling:** Solved SQLite write-locks in a multi-process environment using a custom `timeout=20` connection strategy.
*   **Boot-up UX:** Integrated FastAPI `lifespan` to handle lazy-loading of heavy ML models, providing a `/status` endpoint for the frontend to poll until the system is "Ready".
*   **Extensibility:** Built a dynamic Celery task registration mechanism that automatically scans the `tasks/` directory, allowing new AI pipelines to be added without modifying core config.
*   **Production-Ready RAG:** Moved beyond simple similarity search by implementing a **Hybrid $\rightarrow$ Rerank** pipeline, significantly increasing the Precision@K for complex queries.
