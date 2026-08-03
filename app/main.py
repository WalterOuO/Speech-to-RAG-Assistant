import logging
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

system_status: list[str] = []


from app.db.status_db import init_db

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI 生命週期管理器"""
    msg1 = "👉 系統啟動中：正在初始化 SQLite 狀態資料庫..."
    logger.info(msg1)
    system_status.append(msg1)
    init_db()

    msg2 = "🔹 SQLite 狀態資料庫初始化成功！"
    logger.info(msg2)
    system_status.append(msg2)

    msg3 = "👉 系統啟動中：正在載入 RAG 向量資料庫與 LLM 模型權重，請稍候..."
    logger.info(msg3)
    system_status.append(msg3)

    # 延遲引入，確保載入時能被 lifespan 控管
    from app.api import rag, speech

    # 註冊路由
    app.include_router(speech.router)
    app.include_router(rag.router)

    msg4 = "✨ LLM 與向量資料庫載入完成！後端服務正式對外開放！"
    logger.info(msg4)
    system_status.append(msg4)
    yield

app = FastAPI(title="Speech-to-RAG Assistant", lifespan=lifespan)


# 設定 CORS
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():

    return {
        "status":"healthy",
        "database":"connected",
        "vector_db":"ready",
        "llm":"ready"
    }

@app.get("/status")
def get_system_status():
    ready = len(system_status) > 0 and system_status[-1] == "✨ LLM 與向量資料庫載入完成！後端服務正式對外開放！"
    return {
        "messages": system_status,
        "ready": ready
    }
