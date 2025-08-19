@echo off
ECHO Activating virtual environment...

REM 激活uv创建的虚拟环境
CALL .\.venv\Scripts\activate

ECHO Starting FastAPI server with Uvicorn...

REM 直接使用uvicorn启动，并开启热重载
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

pause