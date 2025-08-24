from fastapi import APIRouter, Depends, HTTPException
from app.services.course_plan import CoursePlanService
from app.services.base import get_user_session, BaseEducationService
from app.core.security import get_current_user_id
from app.db import database as db
from loguru import logger


router = APIRouter()


@router.get(
    "/course-plan",
    summary="获取培养方案课程设置",
    description="从教务系统抓取培养方案页面并解析为结构化数据，优先使用缓存",
    tags=["培养方案"],
)
async def get_course_plan(
    session=Depends(get_user_session), student_id: str = Depends(get_current_user_id)
):
    """
    获取培养方案数据

    从教务系统获取培养方案页面并解析为结构化数据，包含模块信息、课程详情等。
    会优先从缓存中读取，如果缓存不存在或过期，则从教务系统实时获取。

    Args:
        session: 当前用户的教务系统会话（通过依赖注入获取）
        student_id: 当前用户的学号（通过依赖注入获取）

    Returns:
        dict: 包含培养方案数据的响应

    Raises:
        HTTPException: 当获取或解析失败时抛出相应的HTTP异常
    """
    try:
        logger.info(f"开始为学号 {student_id} 获取培养方案数据...")
        result = CoursePlanService.get_course_plan_data(session, student_id)
        logger.info(f"为学号 {student_id} 获取培养方案数据成功")
        return result

    except Exception as e:
        # 使用基础服务类统一处理错误
        http_exception = BaseEducationService.handle_service_error(e, "获取培养方案")
        raise http_exception

    finally:
        BaseEducationService.close_session(session)


@router.post(
    "/course-plan/refresh",
    summary="主动刷新培养方案缓存",
    description="强制从教务系统重新获取培养方案数据并更新缓存",
    tags=["培养方案"],
)
async def refresh_course_plan(student_id: str = Depends(get_current_user_id)):
    """
    主动刷新培养方案缓存

    此接口会删除现有的培养方案缓存，以便下次请求时能从教务系统获取最新的数据。

    Args:
        student_id: 当前用户的学号（通过依赖注入获取）

    Returns:
        dict: 操作结果
    """
    try:
        logger.info(f"收到为学号 {student_id} 刷新培养方案缓存的请求。")
        success = db.delete_course_plan(student_id)
        if success:
            logger.info(f"成功删除学号 {student_id} 的培养方案缓存。")
            return {
                "success": True,
                "message": "培养方案缓存已清除，下次请求将重新获取。",
            }
        else:
            logger.info(f"学号 {student_id} 的培养方案缓存不存在，无需刷新。")
            return {"success": True, "message": "培养方案缓存不存在，无需刷新。"}
    except Exception as e:
        logger.error(f"刷新培养方案缓存失败，学号: {student_id}，错误: {e}")
        raise HTTPException(status_code=500, detail="刷新培养方案缓存失败")
