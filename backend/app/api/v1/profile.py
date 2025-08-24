# app/api/v1/profile.py
from fastapi import APIRouter, Depends
from app.schemas.profile import ProfileResponse
from app.schemas.gpa import ErrorResponse
from app.services.profile import ProfileService
from app.services.base import BaseEducationService, get_user_session
from app.core.security import get_current_user
from loguru import logger
import requests


router = APIRouter()


@router.get(
    "/profile",
    response_model=ProfileResponse,
    summary="获取个人信息",
    description="""
获取当前登录用户的个人基本信息。

**功能说明：**
- 获取学生基本信息：姓名、学号、院系、专业、班级
- 实时从教务系统获取最新信息

**返回信息包括：**
- 学生姓名
- 学生编号
- 所属院系
- 专业名称
- 班级名称

**注意事项：**
- 需要有效的JWT Token认证
- 要求用户已成功登录教务系统
- 数据实时从教务系统获取，保证准确性

**数据来源：**
- 曲阜师范大学教务系统个人信息页面
- URL: `/jsxsd/framework/xsMain_new.jsp`
""",
    tags=["个人信息"],
    responses={
        200: {
            "description": "个人信息获取成功",
            "model": ProfileResponse,
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "个人信息获取成功",
                        "data": {
                            "student_name": "***",
                            "student_id": "2022******",
                            "college": "***学院",
                            "major": "***专业",
                            "class_name": "***班",
                        },
                    }
                }
            },
        },
        401: {
            "description": "未授权访问或Session已失效",
            "model": ErrorResponse,
            "content": {
                "application/json": {"example": {"detail": "Session已失效，请重新登录"}}
            },
        },
        500: {
            "description": "服务器内部错误",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {"detail": "获取个人信息失败: 网络连接超时"}
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
async def get_personal_profile(
    session: requests.Session = Depends(get_user_session),
    current_user_hash: str = Depends(get_current_user),
):
    """
    获取个人信息接口

    获取当前认证用户的个人基本信息，包括姓名、学号、院系、专业、班级等信息。

    Args:
        session: 已登录的教务系统session（通过依赖注入获取）
        current_user_hash: 当前认证用户的hash（通过依赖注入获取）

    Returns:
        ProfileResponse: 包含个人信息的响应对象

    Raises:
        HTTPException: 当获取信息失败时抛出相应的HTTP异常
    """
    logger.info(f"用户 {current_user_hash} 请求获取个人信息")

    try:
        # 使用ProfileService获取个人信息
        result = ProfileService.get_student_profile(session)

        if result["success"]:
            logger.info(f"用户 {current_user_hash} 个人信息获取成功")
            return ProfileResponse(
                success=True, message=result["message"], data=result["data"]
            )
        else:
            logger.warning(
                f"用户 {current_user_hash} 个人信息获取失败: {result['message']}"
            )
            # 根据错误信息抛出相应的异常
            raise BaseEducationService.handle_service_error(
                Exception(result["message"]), "获取个人信息"
            )

    except Exception as e:
        logger.error(f"用户 {current_user_hash} 获取个人信息时发生错误: {e}")
        # 使用基础服务的错误处理方法
        raise BaseEducationService.handle_service_error(e, "获取个人信息")

    finally:
        # 确保session得到正确管理
        BaseEducationService.close_session(session)
