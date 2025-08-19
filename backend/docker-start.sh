#!/bin/bash

# Docker启动脚本

echo "启动Docker服务..."

# 创建数据目录
mkdir -p data

# 设置镜像名称
IMAGE_NAME="easyqfnujw-backend"
CONTAINER_NAME="easyqfnujw-backend"

# 检查镜像是否存在
if ! docker image inspect "$IMAGE_NAME" &> /dev/null; then
    echo "错误：镜像 $IMAGE_NAME 不存在！"
    echo "请先运行 docker-build-export.sh 构建镜像，或运行以下命令导入镜像："
    echo "docker load -i docker-images/$IMAGE_NAME-latest.tar"
    exit 1
fi

# 检查容器是否已经存在并运行
if docker ps -q -f name="$CONTAINER_NAME" &> /dev/null; then
    echo "容器 $CONTAINER_NAME 已在运行中"
    echo "API访问地址: http://localhost:8000"
    echo "API文档: http://localhost:8000/docs"
    exit 0
fi

# 检查容器是否存在但未运行
if docker ps -a -q -f name="$CONTAINER_NAME" &> /dev/null; then
    echo "启动现有容器 $CONTAINER_NAME..."
    docker start "$CONTAINER_NAME"
else
    # 使用docker-compose启动（推荐）
    if command -v docker-compose &> /dev/null; then
        echo "使用docker-compose启动服务..."
        docker-compose -p easyqfnujw up -d
    else
        echo "创建并启动新容器..."
        # 直接使用docker run
        docker run -d \
            --name "$CONTAINER_NAME" \
            -p 8000:8000 \
            -v "$(pwd)/data:/app/data" \
            -e JWT_SECRET_KEY=your-super-secret-key-change-in-production \
            "$IMAGE_NAME"
    fi
fi

if [ $? -eq 0 ]; then
    echo "服务已启动！"
    echo "API访问地址: http://localhost:8000"
    echo "API文档: http://localhost:8000/docs"
else
    echo "启动失败！"
fi

echo ""
echo "查看日志: docker logs easyqfnujw-backend"
echo "停止服务: docker-compose -p easyqfnujw down 或 docker stop easyqfnujw-backend"
