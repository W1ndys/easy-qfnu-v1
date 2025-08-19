#!/bin/bash

# 设置UTF-8编码
export LANG=zh_CN.UTF-8

echo "正在激活虚拟环境..."

# 检查当前目录的虚拟环境目录是否存在
if [ ! -f ".venv/bin/activate" ]; then
    echo "[错误] 未找到虚拟环境，请先运行 python -m venv .venv 创建虚拟环境。"
    read -p "按任意键继续..."
    exit 1
fi

# 激活虚拟环境
source .venv/bin/activate

echo "正在启动 FastAPI 服务器（Uvicorn）..."

# 使用 uvicorn 启动，并开启热重载
python3 -m app.main
# 保持终端打开
read -p "按任意键退出..."
