#!/bin/bash

# Docker构建并导出镜像包脚本

echo "开始构建并导出Docker镜像包..."

# 创建数据目录
mkdir -p data

# 设置镜像名称和版本
IMAGE_NAME="easyqfnujw-backend"
IMAGE_VERSION="latest"
EXPORT_DIR="docker-images"

# 创建导出目录
mkdir -p "$EXPORT_DIR"

echo "构建Docker镜像..."
docker build -t "$IMAGE_NAME:$IMAGE_VERSION" .

if [ $? -ne 0 ]; then
    echo "构建失败！"
    exit 1
fi

echo "导出Docker镜像包..."
docker save -o "$EXPORT_DIR/$IMAGE_NAME-$IMAGE_VERSION.tar" "$IMAGE_NAME:$IMAGE_VERSION"

if [ $? -ne 0 ]; then
    echo "导出失败！"
    exit 1
fi

echo ""
echo "构建完成！"
echo "镜像名称: $IMAGE_NAME:$IMAGE_VERSION"
echo "导出文件: $EXPORT_DIR/$IMAGE_NAME-$IMAGE_VERSION.tar"
echo ""
echo "使用方法:"
echo "1. 传输tar文件到目标机器"
echo "2. 在目标机器上运行: docker load -i $IMAGE_NAME-$IMAGE_VERSION.tar"
echo "3. 运行容器: docker run -d --name $IMAGE_NAME -p 8000:8000 $IMAGE_NAME:$IMAGE_VERSION"
echo ""
