@echo off
setlocal
chcp 65001 >nul
REM --- 配置 ---
set VENV_DIR=.venv
set PYTHON_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

echo [1/4] 正在检查 uv 是否已安装...
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 uv 命令。
    echo 请先通过 'pip install uv' 或 'pipx install uv' 安装。
    goto :eof
)
echo      uv 已安装。

echo [2/4] 正在检查 requirements.txt 文件...
if not exist requirements.txt (
    echo [错误] 未找到 requirements.txt 文件。
    goto :eof
)
echo      requirements.txt 已找到。

echo [3/4] 正在创建虚拟环境 '%VENV_DIR%'...
uv venv %VENV_DIR%
if %errorlevel% neq 0 (
    echo [错误] 创建虚拟环境失败。
    goto :eof
)
echo      虚拟环境创建成功。

echo [4/4] 正在从 %PYTHON_INDEX_URL% 安装依赖...
uv pip install -r requirements.txt --index-url %PYTHON_INDEX_URL%
if %errorlevel% neq 0 (
    echo [错误] 安装依赖失败。
    goto :eof
)
echo      依赖安装成功。

echo.
echo --- 设置完成 ---
echo 虚拟环境已在 '%VENV_DIR%' 文件夹中创建并配置完毕。
echo.
echo 若要激活环境, 请运行:
echo %VENV_DIR%\Scripts\activate
echo.

pause
endlocal