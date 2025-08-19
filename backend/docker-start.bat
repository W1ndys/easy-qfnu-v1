@echo off
chcp 65001 >nul

echo 启动Docker服务...

REM 创建数据目录
if not exist "data" mkdir data

REM 设置镜像名称
set IMAGE_NAME=easyqfnujw-backend
set CONTAINER_NAME=easyqfnujw-backend

REM 检查镜像是否存在
docker image inspect %IMAGE_NAME% >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：镜像 %IMAGE_NAME% 不存在！
    echo 请先运行 docker-build-export.bat 构建镜像，或运行以下命令导入镜像：
    echo docker load -i docker-images\%IMAGE_NAME%-latest.tar
    pause
    exit /b 1
)

REM 检查容器是否已经存在并运行
docker ps -q -f name=%CONTAINER_NAME% >nul 2>&1
if %errorlevel% == 0 (
    echo 容器 %CONTAINER_NAME% 已在运行中
    echo API访问地址: http://localhost:8000
    echo API文档: http://localhost:8000/docs
    pause
    exit /b 0
)

REM 检查容器是否存在但未运行
docker ps -a -q -f name=%CONTAINER_NAME% >nul 2>&1
if %errorlevel% == 0 (
    echo 启动现有容器 %CONTAINER_NAME%...
    docker start %CONTAINER_NAME%
) else (
    REM 检查是否有docker-compose
    docker-compose --version >nul 2>&1
    if %errorlevel% == 0 (
        echo 使用docker-compose启动服务...
        docker-compose up -d
    ) else (
        echo 创建并启动新容器...
        docker run -d ^
            --name %CONTAINER_NAME% ^
            -p 8000:8000 ^
            -v "%cd%\data:/app/data" ^
            -e JWT_SECRET_KEY=your-super-secret-key-change-in-production ^
            %IMAGE_NAME%
    )
)

if %errorlevel% == 0 (
    echo 服务已启动！
    echo API访问地址: http://localhost:8000
    echo API文档: http://localhost:8000/docs
) else (
    echo 启动失败！
)

echo.
echo 查看日志: docker logs easyqfnujw-backend
echo 停止服务: docker-compose down 或 docker stop easyqfnujw-backend
pause
