from fastapi import APIRouter, Depends, HTTPException
from app.services.course_plan_service import CoursePlanService
from app.services.base_service import get_user_session, BaseEducationService
from loguru import logger


router = APIRouter()


@router.get(
    "/course-plan",
    summary="获取培养方案课程设置",
    description="从教务系统抓取培养方案页面并解析为结构化数据",
    tags=["培养方案"],
)
async def get_course_plan(session=Depends(get_user_session)):
    """
    获取培养方案数据

    从教务系统获取培养方案页面并解析为结构化数据，包含模块信息、课程详情等。

    Args:
        session: 当前用户的教务系统会话（通过依赖注入获取）

    Returns:
        dict: 包含培养方案数据的响应

    Raises:
        HTTPException: 当获取或解析失败时抛出相应的HTTP异常
    """
    try:
        logger.info("开始获取培养方案数据...")
        result = CoursePlanService.get_course_plan_data(session)
        logger.info("培养方案数据获取成功")
        return result

    except Exception as e:
        # 使用基础服务类统一处理错误
        http_exception = BaseEducationService.handle_service_error(e, "获取培养方案")
        raise http_exception

    finally:
        BaseEducationService.close_session(session)
