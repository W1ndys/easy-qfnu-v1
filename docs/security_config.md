# JWT 安全配置说明

## 环境变量配置

创建 `.env` 文件并配置以下环境变量：

```bash
# JWT密钥 - 生产环境中必须设置为强密钥
JWT_SECRET_KEY=your-super-secret-jwt-key-at-least-32-characters-long

# Token过期时间（分钟）
ACCESS_TOKEN_EXPIRE_MINUTES=120

# Refresh Token过期时间（天）
REFRESH_TOKEN_EXPIRE_DAYS=7

# 最大登录尝试次数
MAX_LOGIN_ATTEMPTS=5

# IP白名单功能（true/false）
ENABLE_IP_WHITELIST=false

# 允许的IP地址列表（逗号分隔，支持CIDR网段）
# 示例：192.168.1.0/24,10.0.0.1,172.16.0.0/16
ALLOWED_IPS=
```

## 安全功能说明

### 1. 强密钥管理

- 自动生成 64 字符随机密钥
- 支持环境变量配置
- 生产环境必须设置 `JWT_SECRET_KEY`

### 2. Token 安全特性

- Access Token 默认 2 小时过期
- Refresh Token 默认 7 天过期
- 包含 JWT ID（jti）用于追踪和撤销
- 支持 IP 地址绑定验证
- 添加标准 JWT 声明（iat, nbf, exp）

### 3. Token 黑名单机制

- 支持 Token 撤销
- 用户登出时自动加入黑名单
- 防止已撤销 Token 的重复使用

### 4. IP 安全验证

- Token 与 IP 地址绑定
- 支持 IP 白名单功能
- 支持 CIDR 网段配置
- 自动获取真实客户端 IP

### 5. Token 刷新机制

- 安全的 Token 刷新流程
- 自动撤销旧的 Refresh Token
- 防止 Token 重放攻击

## 生产环境安全建议

1. **密钥管理**：

   - 使用至少 32 个字符的强密钥
   - 定期轮换 JWT 密钥
   - 不要在代码中硬编码密钥

2. **网络安全**：

   - 启用 HTTPS
   - 考虑启用 IP 白名单
   - 使用防火墙限制访问

3. **监控和日志**：

   - 监控异常登录行为
   - 记录安全相关事件
   - 设置告警机制

4. **Token 管理**：
   - 使用合适的过期时间
   - 在生产环境中使用 Redis 等持久化存储管理黑名单
   - 考虑实现 Token 降级机制

## 使用示例

### 创建 Token

```python
from app.core.security import create_access_token, create_refresh_token

# 创建 Access Token
access_token = create_access_token(
    data={"sub": "student_id"},
    client_ip="192.168.1.100"
)

# 创建 Refresh Token
refresh_token = create_refresh_token(
    data={"sub": "student_id"},
    client_ip="192.168.1.100"
)
```

### 验证用户

```python
from fastapi import Depends, Request
from app.core.security import get_current_user

@app.get("/protected")
async def protected_route(
    current_user: str = Depends(get_current_user),
    request: Request
):
    # current_user 包含验证通过的学号
    return {"user": current_user}
```

### Token 刷新

```python
from app.core.security import refresh_access_token

# 刷新 Token
new_access_token, new_refresh_token = refresh_access_token(
    refresh_token="old_refresh_token",
    client_ip="192.168.1.100"
)
```

### 用户登出

```python
from app.core.security import logout_user

# 用户登出
logout_user(token="user_access_token")
```
