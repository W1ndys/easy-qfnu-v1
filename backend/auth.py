# auth.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

reusable_oauth2 = HTTPBearer()

SECRET_KEY = "1111"
ALGORITHM = "HS256"


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

        # 直接通过 key 访问，如果 'sub' 不存在，会触发 KeyError
        student_id: str = payload["sub"]

        # 移除了无法访问的 if student_id is None 检查
        return student_id

    except KeyError:
        # 捕获因 payload 中缺少 'sub' 键而产生的错误
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证：Token中缺少用户信息",
        )
    except jwt.ExpiredSignatureError:
        # token过期
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录已过期，请重新登录",
        )
    except jwt.InvalidTokenError:
        # 其他所有无效token的情况（如签名错误）
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
        )
