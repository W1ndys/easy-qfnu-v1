"""
安全相关功能
JWT令牌生成、验证和用户认证
"""

from datetime import datetime, timedelta, UTC
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
import hashlib
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# 密码上下文（虽然我们不存储密码，但可能用于其他加密需求）
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建JWT访问令牌

    Args:
        data: 要编码的数据
        expires_delta: 过期时间间隔

    Returns:
        JWT令牌字符串
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire, "iat": datetime.now(UTC)})

    try:
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    except Exception as e:
        logger.error(f"JWT令牌创建失败: {e}")
        raise


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    验证JWT令牌

    Args:
        token: JWT令牌字符串

    Returns:
        解码后的payload，验证失败返回None
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        # 检查令牌是否过期
        exp = payload.get("exp")
        if exp and datetime.now(UTC) > datetime.fromtimestamp(exp, UTC):
            logger.warning("JWT令牌已过期")
            return None

        return payload
    except jwt.PyJWTError as e:
        logger.warning(f"JWT令牌验证失败: {e}")
        return None
    except Exception as e:
        logger.error(f"JWT令牌验证异常: {e}")
        return None


def hash_string(text: str) -> str:
    """
    对字符串进行哈希处理
    用于敏感信息的单向加密

    Args:
        text: 要哈希的字符串

    Returns:
        哈希后的字符串
    """
    return hashlib.sha256(text.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


class SessionExpiredError(Exception):
    """学校官网Session过期异常"""

    pass
