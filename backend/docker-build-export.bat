@echo off
chcp 65001 >nul

echo 开始构建并导出Docker镜像包...

REM 创建数据目录
if not exist "data" mkdir data

REM 设置镜像名称和版本
set IMAGE_NAME=easyqfnujw-backend
set IMAGE_VERSION=latest
set EXPORT_DIR=docker-images

REM 创建导出目录
if not exist "%EXPORT_DIR%" mkdir "%EXPORT_DIR%"

echo 构建Docker镜像...
docker build -t %IMAGE_NAME%:%IMAGE_VERSION% .

if %errorlevel% neq 0 (
    echo 构建失败！
    pause
    exit /b 1
)

echo 导出Docker镜像包...
docker save -o "%EXPORT_DIR%\%IMAGE_NAME%-%IMAGE_VERSION%.tar" %IMAGE_NAME%:%IMAGE_VERSION%

if %errorlevel% neq 0 (
    echo 导出失败！
    pause
    exit /b 1
)

echo.
echo 构建完成！
echo 镜像名称: %IMAGE_NAME%:%IMAGE_VERSION%
echo 导出文件: %EXPORT_DIR%\%IMAGE_NAME%-%IMAGE_VERSION%.tar
echo.
echo 使用方法:
echo 1. 传输tar文件到目标机器
echo 2. 在目标机器上运行: docker load -i %IMAGE_NAME%-%IMAGE_VERSION%.tar
echo 3. 运行容器: docker run -d --name %IMAGE_NAME% -p 8000:8000 %IMAGE_NAME%:%IMAGE_VERSION%
echo.
pause
