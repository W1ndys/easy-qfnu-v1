#!/bin/bash

# Docker启动脚本

echo "开始构建Docker镜像..."

# 创建数据目录
mkdir -p data

# 构建Docker镜像
docker build -t easyqfnujw-backend .

echo "启动Docker容器..."

# 使用docker-compose启动（推荐）
if command -v docker-compose &> /dev/null; then
    docker-compose up -d
    echo "服务已启动！"
    echo "API访问地址: http://localhost:8000"
    echo "API文档: http://localhost:8000/docs"
else
    # 直接使用docker run
    docker run -d \
        --name easyqfnujw-backend \
        -p 8000:8000 \
        -v $(pwd)/data:/app/data \
        -e JWT_SECRET_KEY=your-super-secret-key-change-in-production \
        easyqfnujw-backend
    
    echo "容器已启动！"
    echo "API访问地址: http://localhost:8000"
    echo "API文档: http://localhost:8000/docs"
fi

echo ""
echo "查看日志: docker logs easyqfnujw-backend"
echo "停止服务: docker-compose down 或 docker stop easyqfnujw-backend"
