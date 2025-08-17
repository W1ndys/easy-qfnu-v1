"""
认证相关API端点
处理用户登录、注册和JWT令牌管理
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from datetime import timedelta
import logging

from app.core.config import settings
from app.core.security import create_access_token, SessionExpiredError
from app.core.database import get_db
from app.services.auth_service import AuthService
from app.models.user import UserCreate, UserLogin, Token

logger = logging.getLogger(__name__)

router = APIRouter()


class LoginRequest(BaseModel):
    """登录请求模型"""

    student_id: str
    password: str


class LoginResponse(BaseModel):
    """登录响应模型"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


@router.post("/login", response_model=LoginResponse, summary="用户登录")
async def login(login_data: LoginRequest, db=Depends(get_db)):
    """
    用户登录接口

    流程：
    1. 验证学号密码（通过学校官网）
    2. 获取并存储学校官网Session
    3. 生成JWT令牌返回给小程序

    注意：密码不会被存储，仅用于获取官网Session
    """
    try:
        auth_service = AuthService(db)

        # 尝试登录学校官网并获取Session
        session_data = await auth_service.authenticate_with_school(
            login_data.student_id, login_data.password
        )

        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="学号或密码错误"
            )

        # 存储Session到数据库
        await auth_service.store_session(login_data.student_id, session_data)

        # 创建或更新用户记录
        user = await auth_service.get_or_create_user(login_data.student_id)

        # 生成JWT令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["student_id"], "user_id": user["id"]},
            expires_delta=access_token_expires,
        )

        logger.info(f"用户 {login_data.student_id} 登录成功")

        return LoginResponse(
            access_token=access_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    except SessionExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="学校官网Session已过期，请重新登录",
        )
    except Exception as e:
        logger.error(f"登录过程发生错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败，请稍后重试",
        )


@router.post("/logout", summary="用户退出")
async def logout(
    current_user: dict = Depends(
        lambda: {"student_id": "test"}
    ),  # TODO: 实现真实的用户依赖
    db=Depends(get_db),
):
    """
    用户退出接口
    清除服务器端存储的Session数据
    """
    try:
        auth_service = AuthService(db)
        await auth_service.clear_session(current_user["student_id"])

        logger.info(f"用户 {current_user['student_id']} 退出登录")

        return {"message": "退出成功"}

    except Exception as e:
        logger.error(f"退出登录过程发生错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="退出失败"
        )


@router.get("/verify", summary="验证令牌")
async def verify_token(
    current_user: dict = Depends(
        lambda: {"student_id": "test"}
    ),  # TODO: 实现真实的用户依赖
):
    """
    验证当前JWT令牌是否有效
    """
    return {"valid": True, "user": current_user}
