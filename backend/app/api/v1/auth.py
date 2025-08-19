# app/api/v1/auth.py
from fastapi import APIRouter, HTTPException
from app.schemas.user import UserLogin, Token
from app.schemas.gpa import ErrorResponse
from app.services.scraper import login_to_university
from app.db.database import save_session

# ⬇️ 导入我们新建的 create_access_token 函数
from app.core.security import create_access_token

router = APIRouter()


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
    tags=["Authentication"],
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
async def login_for_access_token(form_data: UserLogin):
    """
    用户登录接口

    通过学号和密码验证用户身份，成功后返回JWT Token用于后续API认证。

    Args:
        form_data: 包含学号和密码的登录信息

    Returns:
        Token: 包含JWT访问令牌和令牌类型的对象

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

    # ⬇️ 调用封装好的函数来创建Token
    access_token = create_access_token(data={"sub": form_data.student_id})

    return {"access_token": access_token, "token_type": "bearer"}
