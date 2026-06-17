import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# 尋找 tasks 目錄下的所有 .py 檔案，並將它們加入 Celery 的 include 列表
tasks_dir = os.path.join(os.path.dirname(__file__), 'tasks')
dynamic_modules = []

if os.path.exists(tasks_dir):
    for f in os.listdir(tasks_dir):
        # 只要是 .py 結尾，且不是 __init__.py 的檔案，全部抓出來
        if f.endswith('.py') and not f.startswith('__'):
            module_name = f"app.tasks.{f[:-3]}"
            dynamic_modules.append(module_name)

celery = Celery(
    "speech_tasks",
    broker=os.getenv("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0"),
    backend=os.getenv("CELERY_BACKEND_URL", "redis://127.0.0.1:6379/0"),
    include=dynamic_modules
)