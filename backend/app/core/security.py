# app/core/security.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
from typing import Optional

reusable_oauth2 = HTTPBearer()

# --- 安全相关的核心配置 ---
# ⚠️ 在生产环境中，这个密钥应该更复杂，并且从环境变量中读取
SECRET_KEY = "1111"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # Token有效期：7天


# --- [新增] 创建Token的函数 ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    创建一个新的JWT Token。

    Args:
        data: 需要编码到token中的数据字典 (e.g., {"sub": "user_id"})
        expires_delta: 可选的过期时间增量

    Returns:
        编码后的JWT Token字符串
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # 如果没有提供过期时间，就使用默认的分钟数
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# --- [已有] 解码Token的函数 ---
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(reusable_oauth2),
) -> str:
    """
    一个依赖函数 (安检员)。
    验证JWT Token，并返回学号 (student_id)。
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        student_id: str = payload["sub"]
        return student_id

    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证：Token中缺少用户信息",
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录已过期，请重新登录",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
        )
