@echo off
chcp 65001 >nul

ECHO 正在激活虚拟环境...

REM 检查当前目录的虚拟环境目录是否存在
IF NOT EXIST ".venv\Scripts\activate" (
    ECHO [错误] 未找到虚拟环境，请先运行 python -m venv .venv 创建虚拟环境。
    pause
    exit /b 1
)

CALL .venv\Scripts\activate

ECHO 正在启动 FastAPI 服务器（Uvicorn）...

REM 使用 uvicorn 启动，并开启热重载
python -m app.main

pause