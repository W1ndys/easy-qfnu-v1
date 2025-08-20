# app/core/security.py

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Set
import ipaddress
from loguru import logger

reusable_oauth2 = HTTPBearer()

# --- 安全相关的核心配置 ---
# 从环境变量读取配置，如果没有则生成安全的默认值
_secret_key = os.getenv("JWT_SECRET_KEY")
if not _secret_key:
    # 生成一个强密钥（生产环境中应该设置环境变量）
    _secret_key = secrets.token_urlsafe(64)
    logger.warning(
        "⚠️  警告：正在使用自动生成的JWT密钥。在生产环境中请设置JWT_SECRET_KEY环境变量！"
    )

# 确保SECRET_KEY是字符串类型
SECRET_KEY: str = _secret_key

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120")
)  # 默认2小时
REFRESH_TOKEN_EXPIRE_DAYS = int(
    os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
)  # 刷新Token 7天

logger.info(
    f"安全配置加载完成: 算法={ALGORITHM}, Access Token过期时间={ACCESS_TOKEN_EXPIRE_MINUTES}分钟, Refresh Token过期时间={REFRESH_TOKEN_EXPIRE_DAYS}天"
)

# Token黑名单（在生产环境中应该使用Redis等持久化存储）
BLACKLISTED_TOKENS: Set[str] = set()

# 安全配置
MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
ENABLE_IP_WHITELIST = os.getenv("ENABLE_IP_WHITELIST", "false").lower() == "true"
ALLOWED_IPS = (
    os.getenv("ALLOWED_IPS", "").split(",") if os.getenv("ALLOWED_IPS") else []
)

logger.info(
    f"安全策略配置: 最大登录尝试次数={MAX_LOGIN_ATTEMPTS}, IP白名单={ENABLE_IP_WHITELIST}, 允许的IP数量={len(ALLOWED_IPS)}"
)


# --- Token管理函数 ---
def generate_token_id() -> str:
    """生成唯一的Token ID用于追踪和撤销"""
    token_id = secrets.token_urlsafe(16)
    logger.debug(f"生成新的Token ID: {token_id}")
    return token_id


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
    client_ip: Optional[str] = None,
) -> str:
    """
    创建一个新的JWT Access Token。

    Args:
        data: 需要编码到token中的数据字典 (e.g., {"sub": "user_id"})
        expires_delta: 可选的过期时间增量
        client_ip: 客户端IP地址（用于IP绑定）

    Returns:
        编码后的JWT Token字符串
    """
    logger.debug(
        f"开始创建Access Token，用户: {data.get('sub', 'unknown')}, IP: {client_ip}"
    )

    to_encode = data.copy()
    now = datetime.now(timezone.utc)

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # 添加标准JWT声明和自定义安全字段
    to_encode.update(
        {
            "exp": expire,  # 过期时间
            "iat": now,  # 签发时间
            "nbf": now,  # 生效时间
            "jti": generate_token_id(),  # JWT ID，用于追踪和撤销
            "type": "access",  # Token类型
            "ip_hash": (
                hashlib.sha256(client_ip.encode()).hexdigest() if client_ip else None
            ),  # IP哈希
        }
    )

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(
        f"Access Token创建成功，用户: {data.get('sub', 'unknown')}, 过期时间: {expire.isoformat()}"
    )
    return encoded_jwt


def create_refresh_token(data: dict, client_ip: Optional[str] = None) -> str:
    """
    创建一个新的JWT Refresh Token。

    Args:
        data: 需要编码到token中的数据字典
        client_ip: 客户端IP地址

    Returns:
        编码后的JWT Refresh Token字符串
    """
    logger.debug(
        f"开始创建Refresh Token，用户: {data.get('sub', 'unknown')}, IP: {client_ip}"
    )

    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update(
        {
            "exp": expire,
            "iat": now,
            "nbf": now,
            "jti": generate_token_id(),
            "type": "refresh",
            "ip_hash": (
                hashlib.sha256(client_ip.encode()).hexdigest() if client_ip else None
            ),
        }
    )

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(
        f"Refresh Token创建成功，用户: {data.get('sub', 'unknown')}, 过期时间: {expire.isoformat()}"
    )
    return encoded_jwt


# --- Token验证和管理函数 ---
def blacklist_token(token: str) -> None:
    """将Token添加到黑名单"""
    logger.info(f"将Token加入黑名单: {token[:20]}...")
    BLACKLISTED_TOKENS.add(token)
    logger.debug(f"当前黑名单Token数量: {len(BLACKLISTED_TOKENS)}")


def is_token_blacklisted(token: str) -> bool:
    """检查Token是否在黑名单中"""
    is_blacklisted = token in BLACKLISTED_TOKENS
    if is_blacklisted:
        logger.warning(f"检测到黑名单Token: {token[:20]}...")
    return is_blacklisted


def validate_ip_address(client_ip: str, token_ip_hash: Optional[str]) -> bool:
    """验证客户端IP是否匹配Token中的IP哈希"""
    if not token_ip_hash:
        logger.debug("Token中没有IP哈希，跳过IP验证")
        return True  # 如果Token中没有IP哈希，则跳过验证

    current_ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()
    is_valid = current_ip_hash == token_ip_hash

    if is_valid:
        logger.debug(f"IP地址验证通过: {client_ip}")
    else:
        logger.warning(
            f"IP地址验证失败: 当前IP={client_ip}, Token中IP哈希={token_ip_hash[:16]}..."
        )

    return is_valid


def check_ip_whitelist(client_ip: str) -> bool:
    """检查IP是否在白名单中"""
    if not ENABLE_IP_WHITELIST or not ALLOWED_IPS:
        logger.debug("IP白名单未启用，跳过检查")
        return True

    try:
        client_addr = ipaddress.ip_address(client_ip)
        for allowed_ip in ALLOWED_IPS:
            allowed_ip = allowed_ip.strip()
            if not allowed_ip:
                continue

            # 支持单个IP和CIDR网段
            if "/" in allowed_ip:
                if client_addr in ipaddress.ip_network(allowed_ip, strict=False):
                    logger.debug(f"IP {client_ip} 在白名单网段 {allowed_ip} 中")
                    return True
            else:
                if client_addr == ipaddress.ip_address(allowed_ip):
                    logger.debug(f"IP {client_ip} 在白名单中")
                    return True

        logger.warning(f"IP {client_ip} 不在白名单中")
        return False
    except (ipaddress.AddressValueError, ValueError) as e:
        logger.error(f"IP地址验证出错: {e}")
        return False


def decode_and_validate_token(
    token: str, client_ip: Optional[str] = None, token_type: str = "access"
) -> dict:
    """
    解码并验证JWT Token的完整性和安全性。

    Args:
        token: JWT Token字符串
        client_ip: 客户端IP地址
        token_type: Token类型 ("access" 或 "refresh")

    Returns:
        解码后的payload字典

    Raises:
        HTTPException: 当Token无效时
    """
    logger.debug(f"开始验证Token，类型: {token_type}, IP: {client_ip}")

    # 检查Token是否在黑名单中
    if is_token_blacklisted(token):
        logger.warning("Token在黑名单中，验证失败")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token已被撤销，请重新登录",
        )

    try:
        # 解码JWT Token
        logger.debug("正在解码JWT Token...")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # 验证Token类型
        if payload.get("type") != token_type:
            logger.warning(
                f"Token类型不匹配，期望: {token_type}, 实际: {payload.get('type')}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"无效的Token类型，期望：{token_type}",
            )

        # 验证必要字段
        if "sub" not in payload:
            logger.error("Token中缺少用户信息字段")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token中缺少用户信息",
            )

        # IP地址验证
        if client_ip:
            # 检查IP白名单
            if not check_ip_whitelist(client_ip):
                logger.warning(f"IP {client_ip} 不在白名单中")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="访问被拒绝：IP地址不在允许列表中",
                )

            # 验证IP绑定
            token_ip_hash = payload.get("ip_hash")
            if not validate_ip_address(client_ip, token_ip_hash):
                logger.warning(f"IP地址绑定验证失败: {client_ip}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token与当前IP地址不匹配",
                )

        logger.info(f"Token验证成功，用户: {payload.get('sub')}, 类型: {token_type}")
        return payload

    except jwt.ExpiredSignatureError:
        logger.warning("Token已过期")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token已过期，请重新登录",
        )
    except jwt.InvalidTokenError as e:
        logger.error(f"Token无效: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(reusable_oauth2),
) -> str:
    """
    基础的用户认证依赖函数。
    验证JWT Token并返回学号 (student_id)。

    注意：此版本不包含IP验证，如需IP验证请使用 get_current_user_with_ip
    """
    logger.debug("使用基础用户认证（无IP验证）")
    token = credentials.credentials
    payload = decode_and_validate_token(token, None, "access")
    return payload["sub"]


def get_current_user_with_ip(
    credentials: HTTPAuthorizationCredentials = Depends(reusable_oauth2),
    request: Request = Depends(),
) -> str:
    """
    增强的用户认证依赖函数，包含IP验证。
    验证JWT Token并返回学号 (student_id)。
    """
    logger.debug("使用增强用户认证（包含IP验证）")
    token = credentials.credentials
    client_ip = None

    # 获取客户端IP地址
    if request and request.client:
        # 优先使用代理头中的真实IP
        client_ip = (
            request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
            or request.headers.get("X-Real-IP")
            or getattr(request.client, "host", None)
        )
        logger.debug(f"检测到客户端IP: {client_ip}")

    payload = decode_and_validate_token(token, client_ip, "access")
    return payload["sub"]


def refresh_access_token(
    refresh_token: str, client_ip: Optional[str] = None
) -> tuple[str, str]:
    """
    使用Refresh Token刷新Access Token。

    Args:
        refresh_token: Refresh Token字符串
        client_ip: 客户端IP地址

    Returns:
        新的(access_token, refresh_token)元组
    """
    logger.info(f"开始刷新Access Token，IP: {client_ip}")

    # 验证Refresh Token
    payload = decode_and_validate_token(refresh_token, client_ip, "refresh")

    # 撤销旧的Refresh Token
    logger.debug("撤销旧的Refresh Token")
    blacklist_token(refresh_token)

    # 创建新的Token对
    user_data = {"sub": payload["sub"]}
    new_access_token = create_access_token(user_data, client_ip=client_ip)
    new_refresh_token = create_refresh_token(user_data, client_ip=client_ip)

    logger.info(f"Token刷新成功，用户: {payload['sub']}")
    return new_access_token, new_refresh_token


def logout_user(token: str) -> None:
    """
    用户登出，将Token加入黑名单。

    Args:
        token: 要撤销的Token
    """
    logger.info(f"用户登出，撤销Token: {token[:20]}...")
    blacklist_token(token)
