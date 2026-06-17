FROM python:3.11-slim

# Whisper 需要 ffmpeg 處理音訊，需安裝
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 複製依賴清單並安裝
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案內的所有程式碼與檔案
COPY . .

# 啟動 FastAPI (這個指令會在 docker-compose 中被覆寫或設定)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]