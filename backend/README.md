# Easy-QFNU 后端项目

Easy-QFNU 是一个基于 FastAPI 的曲阜师范大学教务辅助工具后端服务。

## 项目特点

- 🚀 **高性能**: 基于 FastAPI 框架，提供高性能的 API 服务
- 🔒 **安全可靠**: JWT 认证、HTTPS 加密、Session 管理
- 📊 **数据丰富**: 成绩查询、课表获取、数据统计分析
- 🏗️ **架构清晰**: 分层架构，代码结构清晰易维护
- 📱 **小程序友好**: 专为微信小程序设计的 API 接口

## 技术栈

- **框架**: FastAPI 0.104.1
- **数据库**: SQLite 3
- **认证**: JWT (PyJWT)
- **HTTP客户端**: Requests
- **数据验证**: Pydantic
- **密码加密**: Passlib + bcrypt
- **HTML解析**: BeautifulSoup4

## 项目结构

```
backend/
├── app/
│   ├── api/v1/          # API 路由
│   │   ├── auth.py      # 认证相关接口
│   │   ├── grades.py    # 成绩查询接口
│   │   ├── schedule.py  # 课表查询接口
│   │   └── stats.py     # 数据统计接口
│   ├── core/            # 核心模块
│   │   ├── config.py    # 配置文件
│   │   ├── database.py  # 数据库管理
│   │   └── security.py  # 安全相关
│   ├── models/          # 数据模型
│   │   ├── user.py      # 用户模型
│   │   ├── grade.py     # 成绩模型
│   │   ├── schedule.py  # 课表模型
│   │   └── stats.py     # 统计模型
│   ├── services/        # 业务逻辑
│   │   ├── auth_service.py      # 认证服务
│   │   ├── grade_service.py     # 成绩服务
│   │   ├── schedule_service.py  # 课表服务
│   │   └── stats_service.py     # 统计服务
│   └── data/            # 数据存储目录
├── main.py              # 应用入口
├── requirements.txt     # 依赖包
└── env.example         # 环境变量示例
```

## 快速开始

### 1. 环境准备

确保您的系统已安装：
- Python 3.8+
- pip

### 2. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 环境配置

复制环境变量示例文件并配置：

```bash
cp env.example .env
```

编辑 `.env` 文件，修改相应配置：

```env
# 重要：生产环境必须修改密钥
SECRET_KEY=your-very-secret-key-change-in-production

# 学校教务系统URL（根据实际情况调整）
QFNU_LOGIN_URL=http://jwgl.qfnu.edu.cn/jsxsd/xk/LoginToXk
QFNU_GRADE_URL=http://jwgl.qfnu.edu.cn/jsxsd/kscj/cjcx_list
QFNU_SCHEDULE_URL=http://jwgl.qfnu.edu.cn/jsxsd/xskb/xskb_list.do
```

### 4. 启动服务

开发环境：
```bash
python main.py
```

生产环境：
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 5. 访问文档

启动后访问：
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## API 接口

### 认证接口

- `POST /api/login` - 用户登录
- `POST /api/logout` - 用户退出
- `GET /api/verify` - 验证令牌

### 成绩接口

- `GET /api/grades` - 获取个人成绩
- `GET /api/grades/summary` - 获取成绩摘要

### 课表接口

- `GET /api/schedule` - 获取个人课表
- `GET /api/schedule/today` - 获取今日课程
- `GET /api/courses/{course_id}/capacity` - 查询课余量

### 统计接口

- `GET /api/stats/course/` - 查询课程统计
- `POST /api/stats/grades/contribute` - 贡献成绩数据
- `GET /api/stats/class_rank/` - 获取班内排名
- `POST /api/stats/contribution/preference` - 设置贡献偏好

## 数据库

项目使用 SQLite 数据库，包含以下表：

- `users` - 用户信息表
- `sessions` - 会话管理表
- `historical_course_stats` - 历史课程统计表
- `course_statistics` - 用户贡献的成绩统计表

数据库会在首次启动时自动创建。

## 部署

### 生产环境部署

1. **安装依赖**
```bash
pip install -r requirements.txt
```

2. **配置环境变量**
```bash
export SECRET_KEY="your-production-secret-key"
export DEBUG=False
```

3. **使用 Uvicorn 部署**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

4. **使用 Nginx 反向代理**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Docker 部署

创建 `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

构建和运行：
```bash
docker build -t Easy-QFNU-backend .
docker run -p 8000:8000 Easy-QFNU-backend
```

## 安全特性

- **JWT 认证**: 使用 JWT 令牌进行用户认证
- **密码安全**: 不存储用户密码，仅用于获取官网 Session
- **Session 管理**: 加密存储学校官网 Session 数据
- **HTTPS 支持**: 生产环境强制使用 HTTPS
- **数据隔离**: 用户数据严格隔离，确保隐私安全

## 开发指南

### 代码规范

- 使用 `black` 进行代码格式化
- 使用 `isort` 整理导入顺序
- 使用 `flake8` 进行代码检查
- 使用 `mypy` 进行类型检查

运行检查：
```bash
black .
isort .
flake8 .
mypy .
```

### 添加新功能

1. 在 `app/models/` 中定义数据模型
2. 在 `app/services/` 中实现业务逻辑
3. 在 `app/api/v1/` 中添加 API 端点
4. 在 `main.py` 中注册路由

### 测试

```bash
# 安装测试依赖
pip install pytest pytest-asyncio httpx

# 运行测试
pytest
```

## 常见问题

### Q: 如何修改学校教务系统 URL？

A: 在 `.env` 文件中修改 `QFNU_LOGIN_URL`、`QFNU_GRADE_URL` 等配置项。

### Q: 数据库文件存储在哪里？

A: 默认存储在 `app/data/easyqfnujw.db`，可通过 `DATABASE_URL` 配置修改。

### Q: 如何重置数据库？

A: 删除数据库文件后重启应用即可自动重建。

### Q: Session 过期如何处理？

A: 系统会自动检测 Session 状态，过期时返回 401 错误，前端收到后会要求重新登录。

## 许可证

MIT License

## 联系我们

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件至 support@example.com
- 加入 QQ 群：123456789

---

**注意**: 本项目为第三方教务辅助工具，与学校官方无关。请遵守学校相关规定使用。
