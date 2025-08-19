@echo off
chcp 65001 >nul

echo 开始构建Docker镜像...

REM 创建数据目录
if not exist "data" mkdir data

REM 构建Docker镜像
docker build -t easyqfnujw-backend .

echo 启动Docker容器...

REM 检查是否有docker-compose
docker-compose --version >nul 2>&1
if %errorlevel% == 0 (
    docker-compose up -d
    echo 服务已启动！
    echo API访问地址: http://localhost:8000
    echo API文档: http://localhost:8000/docs
) else (
    REM 直接使用docker run
    docker run -d ^
        --name easyqfnujw-backend ^
        -p 8000:8000 ^
        -v "%cd%\data:/app/data" ^
        -e JWT_SECRET_KEY=your-super-secret-key-change-in-production ^
        easyqfnujw-backend
    
    echo 容器已启动！
    echo API访问地址: http://localhost:8000
    echo API文档: http://localhost:8000/docs
)

echo.
echo 查看日志: docker logs easyqfnujw-backend
echo 停止服务: docker-compose down 或 docker stop easyqfnujw-backend
pause
