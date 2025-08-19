# app/api/v1/auth.py
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas.user import UserLogin, Token, RefreshTokenRequest, TokenResponse
from app.schemas.gpa import ErrorResponse
from app.services.scraper import login_to_university
from app.db.database import save_session

# 导入安全相关函数
from app.core.security import (
    create_access_token,
    create_refresh_token,
    refresh_access_token,
    logout_user,
    get_current_user,
    get_current_user_with_ip,
)

router = APIRouter()
security = HTTPBearer()


def get_client_ip(request: Request) -> str:
    """获取客户端真实IP地址"""
    # 优先使用代理头中的真实IP
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # 最后使用直连IP
    return (
        getattr(request.client, "host", "127.0.0.1") if request.client else "127.0.0.1"
    )


@router.post(
    "/login",
    response_model=Token,
    summary="用户登录获取JWT Token",
    description="""
通过学号和密码登录曲阜师范大学教务系统，验证成功后返回JWT Token。

**登录流程：**
1. 验证学号和密码格式
2. 访问教务系统进行身份验证（包括验证码识别）
3. 保存登录会话信息到数据库
4. 生成并返回JWT Token用于后续API调用

**注意事项：**
- Token有效期为系统配置的时长
- Token需要在后续API调用中通过Authorization Bearer方式传递
- 同一用户重新登录会覆盖之前的会话信息

**错误处理：**
- 学号或密码错误时返回401状态码
- 教务系统访问异常时返回503状态码
""",
    tags=["认证"],
    responses={
        200: {
            "description": "登录成功，返回JWT Token",
            "model": Token,
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                    }
                }
            },
        },
        401: {
            "description": "学号或密码错误",
            "model": ErrorResponse,
            "content": {
                "application/json": {"example": {"detail": "学号或密码错误，登录失败"}}
            },
        },
        422: {
            "description": "请求参数格式错误",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "student_id"],
                                "msg": "field required",
                                "type": "value_error.missing",
                            }
                        ]
                    }
                }
            },
        },
        503: {
            "description": "教务系统服务不可用",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {"detail": "教务系统连接失败，请稍后重试"}
                }
            },
        },
    },
)
async def login_for_access_token(form_data: UserLogin, request: Request):
    """
    用户登录接口

    通过学号和密码验证用户身份，成功后返回JWT Token用于后续API认证。

    Args:
        form_data: 包含学号和密码的登录信息
        request: HTTP请求对象，用于获取客户端IP

    Returns:
        Token: 包含JWT访问令牌、刷新令牌和令牌类型的对象

    Raises:
        HTTPException: 登录失败时抛出相应的HTTP异常
    """
    session = login_to_university(
        student_id=form_data.student_id, password=form_data.password
    )

    if session is None:
        raise HTTPException(status_code=401, detail="学号或密码错误，登录失败")

    try:
        # 登录成功后，将 session 的 cookies 保存到数据库
        save_session(student_id=form_data.student_id, session_obj=session)
    finally:
        session.close()

    # 获取客户端IP地址
    client_ip = get_client_ip(request)

    # 创建Token对
    user_data = {"sub": form_data.student_id}
    access_token = create_access_token(user_data, client_ip=client_ip)
    refresh_token = create_refresh_token(user_data, client_ip=client_ip)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 120 * 60,  # 2小时，以秒为单位
    }


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="刷新访问令牌",
    description="""
使用Refresh Token获取新的Access Token和Refresh Token。

**使用场景：**
- 当Access Token即将过期或已过期时
- 实现无感知的Token续期机制

**安全特性：**
- 验证Refresh Token的有效性
- 自动撤销旧的Refresh Token
- IP地址绑定验证
- 生成新的Token对

**注意事项：**
- 旧的Refresh Token在使用后会立即失效
- 需要保存新返回的Token对
- 保持与原登录相同的IP地址（如启用IP绑定）
""",
    tags=["认证"],
    responses={
        200: {
            "description": "Token刷新成功",
            "model": TokenResponse,
        },
        401: {
            "description": "Refresh Token无效或已过期",
            "model": ErrorResponse,
        },
        403: {
            "description": "IP地址验证失败",
            "model": ErrorResponse,
        },
    },
)
async def refresh_token(token_data: RefreshTokenRequest, request: Request):
    """
    刷新访问令牌

    使用有效的Refresh Token获取新的Access Token和Refresh Token对。

    Args:
        token_data: 包含refresh_token的请求数据
        request: HTTP请求对象，用于获取客户端IP

    Returns:
        TokenResponse: 新的Token对和相关信息

    Raises:
        HTTPException: Token无效或刷新失败时抛出HTTP异常
    """
    client_ip = get_client_ip(request)

    try:
        new_access_token, new_refresh_token = refresh_access_token(
            token_data.refresh_token, client_ip=client_ip
        )

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": 120 * 60,  # 2小时，以秒为单位
        }
    except HTTPException:
        # 直接重新抛出HTTPException
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token刷新失败: {str(e)}")


@router.post(
    "/logout",
    summary="用户登出",
    description="""
用户登出，撤销当前的访问令牌。

**功能说明：**
- 将当前Token加入黑名单
- 立即使Token失效
- 安全地结束用户会话

**安全特性：**
- 防止已登出Token的重复使用
- 即时生效的Token撤销

**注意事项：**
- 登出后需要重新登录获取新Token
- 建议前端清除本地存储的Token
- Refresh Token也会一并失效
""",
    tags=["认证"],
    responses={
        200: {
            "description": "登出成功",
            "content": {"application/json": {"example": {"message": "登出成功"}}},
        },
        401: {
            "description": "Token无效或已过期",
            "model": ErrorResponse,
        },
    },
)
async def logout(
    current_user: str = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    用户登出

    撤销当前访问令牌，使其立即失效。

    Args:
        credentials: HTTP Bearer认证凭据
        current_user: 当前认证用户（通过依赖注入获取）

    Returns:
        dict: 登出成功消息

    Raises:
        HTTPException: Token无效时抛出HTTP异常
    """
    token = credentials.credentials

    try:
        logout_user(token)
        return {"message": "登出成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"登出失败: {str(e)}")


@router.get(
    "/me",
    summary="获取当前用户信息",
    description="""
获取当前认证用户的基本信息。

**功能说明：**
- 验证访问令牌
- 返回用户基本信息
- 用于验证Token有效性

**安全特性：**
- 全面的Token验证
- IP地址绑定检查
- 黑名单验证
""",
    tags=["认证"],
    responses={
        200: {
            "description": "用户信息获取成功",
            "content": {
                "application/json": {
                    "example": {"student_id": "20210001", "is_authenticated": True}
                }
            },
        },
        401: {
            "description": "Token无效或已过期",
            "model": ErrorResponse,
        },
    },
)
async def get_current_user_info(current_user: str = Depends(get_current_user)):
    """
    获取当前用户信息

    返回当前认证用户的基本信息。

    Args:
        current_user: 当前认证用户的学号

    Returns:
        dict: 用户基本信息
    """
    return {"student_id": current_user, "is_authenticated": True}
