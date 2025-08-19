# 使用官方Python运行时作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LANG=zh_CN.UTF-8 \
    LC_ALL=zh_CN.UTF-8

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    locales \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 生成中文locale
RUN sed -i '/zh_CN.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen

# 复制requirements文件
COPY requirements.txt .

# 使用国内镜像源安装Python依赖（这是主要瓶颈）
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制应用代码
COPY app/ ./app/

# 创建数据目录（用于SQLite数据库持久化）
RUN mkdir -p /app/data

# 暴露端口
EXPOSE 8000

# 创建非root用户以提高安全性
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# 启动命令
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]