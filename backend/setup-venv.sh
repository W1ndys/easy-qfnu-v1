#!/bin/bash

# --- 配置 ---
VENV_DIR=".venv"
PYTHON_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple"

echo "[1/4] 正在检查 uv 是否已安装..."
if ! command -v uv &> /dev/null; then
    echo "[错误] 未找到 uv 命令。"
    echo "请先通过 'pip install uv' 或 'pipx install uv' 安装。"
    exit 1
fi
echo "     uv 已安装。"

echo "[2/4] 正在检查 requirements.txt 文件..."
if [ ! -f "requirements.txt" ]; then
    echo "[错误] 未找到 requirements.txt 文件。"
    exit 1
fi
echo "     requirements.txt 已找到。"

echo "[3/4] 正在创建虚拟环境 '$VENV_DIR'..."
uv venv "$VENV_DIR" || { echo "[错误] 创建虚拟环境失败。"; exit 1; }
echo "     虚拟环境创建成功。"

echo "[4/4] 正在从 $PYTHON_INDEX_URL 安装依赖..."
uv pip install -r requirements.txt --index-url "$PYTHON_INDEX_URL" || { echo "[错误] 安装依赖失败。"; exit 1; }
echo "     依赖安装成功。"

echo ""
echo "--- 设置完成 ---"
echo "虚拟环境已在 '$VENV_DIR' 文件夹中创建并配置完毕。"
echo ""
echo "若要激活环境, 请运行:"
echo "source $VENV_DIR/bin/activate"
echo ""