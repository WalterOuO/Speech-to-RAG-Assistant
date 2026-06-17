from dotenv import load_dotenv
from fastapi import FastAPI
from app.api import rag, speech
from app.db.status_db import init_db
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(title="Speech-to-RAG Assistant")

@app.on_event("startup")
def startup_event():
    print("正在初始化 SQLite 狀態資料庫...")
    init_db()
    print("SQLite 狀態資料庫初始化成功！")


app.include_router(rag.router)
app.include_router(speech.router)

# 設定 CORS
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to Speech-to-RAG Assistant!"}

