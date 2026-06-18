import sqlite3
import os
from app.config import settings

DB_PATH = settings.DB_PATH

def init_db():
    """初始化資料庫，建立狀態表"""
    with sqlite3.connect(DB_PATH, timeout=20) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audio_status (
                filename TEXT PRIMARY KEY,
                task_id TEXT,
                status TEXT
            )
        """)
        conn.commit()

def update_status(filename: str, task_id: str, status: str):
    """新增或更新音訊檔的狀態"""
    with sqlite3.connect(DB_PATH, timeout=20) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audio_status (filename, task_id, status)
            VALUES (?, ?, ?)
            ON CONFLICT(filename) DO UPDATE SET
                task_id = excluded.task_id,
                status = excluded.status
        """, (filename, task_id, status))
        conn.commit()

def get_status(filename: str):
    """根據檔名查詢狀態"""
    with sqlite3.connect(DB_PATH, timeout=20) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status, task_id FROM audio_status WHERE filename = ?", (filename,))
        row = cursor.fetchone()
        if row:
            return {"status": row[0], "task_id": row[1]}
        return None