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


from app.db.status_db import init_db

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI 生命週期管理器"""
    logger.info("👉 系統啟動中：正在初始化 SQLite 狀態資料庫...")
    init_db()
    logger.info("🔹 SQLite 狀態資料庫初始化成功！")

    logger.info("👉 系統啟動中：正在載入 RAG 向量資料庫與 LLM 模型權重，請稍候...")

    # 延遲引入，確保載入時能被 lifespan 控管
    from app.api import rag, speech

    # 註冊路由
    app.include_router(speech.router)
    app.include_router(rag.router)

    logger.info("✨ LLM 與向量資料庫載入完成！後端服務正式對外開放！")
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

