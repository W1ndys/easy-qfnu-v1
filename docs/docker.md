# EasyQFNUJW Backend Docker 部署指南

## 快速开始

### 1. 准备工作

确保已安装 Docker 和 Docker Compose：

```bash
# 检查Docker
docker --version

# 检查Docker Compose
docker-compose --version
```

### 2. 构建并启动服务

#### Linux/macOS:

```bash
chmod +x docker-start.sh
./docker-start.sh
```

#### Windows:

```cmd
docker-start.bat
```

#### 手动启动:

```bash
# 构建镜像
docker build -t easyqfnujw-backend .

# 使用docker-compose启动
docker-compose up -d

# 或直接使用docker run
docker run -d \
  --name easyqfnujw-backend \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e JWT_SECRET_KEY=your-secret-key \
  easyqfnujw-backend
```

### 3. 访问服务

- API 服务: http://localhost:8000
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/

### 4. 常用命令

```bash
# 查看容器状态
docker ps

# 查看日志
docker logs easyqfnujw-backend

# 进入容器
docker exec -it easyqfnujw-backend bash

# 停止服务
docker-compose down
# 或
docker stop easyqfnujw-backend

# 重启服务
docker-compose restart
```

## 配置说明

### 环境变量

创建 `.env` 文件（参考 `.env.example`）：

```env
JWT_SECRET_KEY=your-super-secret-key-change-in-production
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### 数据持久化

- SQLite 数据库文件存储在 `./data/` 目录
- 该目录会自动挂载到容器中的 `/app/data/`

### 端口配置

- 默认端口: 8000
- 可通过修改 `docker-compose.yml` 中的端口映射来更改

## 生产环境部署

### 1. 使用 Nginx 反向代理

```bash
# 启动包含nginx的完整服务
docker-compose --profile with-nginx up -d
```

### 2. 安全配置

- 修改 `JWT_SECRET_KEY` 为强密钥
- 配置适当的 CORS 域名
- 考虑使用外部数据库替代 SQLite

### 3. 监控和日志

```bash
# 实时查看日志
docker-compose logs -f backend

# 查看资源使用
docker stats easyqfnujw-backend
```

## 故障排除

### 常见问题

1. **端口冲突**

   ```bash
   # 更改端口映射
   docker run -p 8001:8000 ...
   ```

2. **权限问题**

   ```bash
   # 确保数据目录权限
   chmod 755 data/
   ```

3. **容器无法启动**
   ```bash
   # 查看详细错误
   docker logs easyqfnujw-backend
   ```

### 重建镜像

```bash
# 强制重建
docker-compose build --no-cache

# 清理旧镜像
docker image prune -f
```

```

## 总结

我已经为你的后端创建了完整的Docker化配置：

### 创建的文件：
1. **`Dockerfile`** - 基于Python 3.11的Docker镜像
2. **`.dockerignore`** - 排除不必要的文件
3. **`docker-compose.yml`** - 编排配置，包含可选的nginx
4. **`.env.example`** - 环境变量模板
5. **`nginx.conf`** - Nginx反向代理配置
6. **`docker-start.sh/.bat`** - 一键启动脚本
7. **`README-Docker.md`** - 详细的使用说明

### 主要特性：
- ✅ 支持中文环境
- ✅ 数据持久化（SQLite数据库）
- ✅ 健康检查
- ✅ 非root用户运行（安全）
- ✅ 可选的Nginx反向代理
- ✅ 环境变量配置
- ✅ 跨平台启动脚本

### 使用方法：
1. 进入backend目录
2. 运行 `./docker-start.sh`（Linux/macOS）或 `docker-start.bat`（Windows）
3. 访问 http://localhost:8000

这样你的后端就完全Docker化了，便于部署和分发！
```
