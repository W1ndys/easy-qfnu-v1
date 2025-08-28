# app/api/v1/classtable.py
from fastapi import APIRouter, Depends, Query, HTTPException
from loguru import logger
import requests
from datetime import datetime

from app.services.classtable import ClassTableService
from app.services.base import get_user_session
from app.schemas.classtable import DayClassTableResponse, WeekClassTableResponse

# 创建路由器
router = APIRouter()


@router.get(
    "/classtable/today",
    response_model=DayClassTableResponse,
    summary="获取今天的课程表",
    description="获取今天的课程表",
    tags=["课程表"],
)
async def get_today_classtable(session: requests.Session = Depends(get_user_session)):
    """
    获取今天的课程表

    自动获取当前日期的课程信息，包括：
    - 课程名称
    - 课程学分
    - 课程属性
    - 上课时间
    - 上课地点
    - 课堂名称
    """
    try:
        # 获取当前日期
        today = datetime.now().strftime("%Y-%m-%d")
        logger.info(f"收到今日课程表查询请求，日期: {today}")

        # 调用服务获取当天课程
        day_courses = ClassTableService.get_day_courses(session, today)

        logger.info(
            f"今日课程表查询成功，日期: {today}, 课程数: {len(day_courses.courses)}"
        )
        return DayClassTableResponse(
            success=True, message="今日课程表获取成功", data=day_courses
        )

    except Exception as e:
        logger.error(f"今日课程表查询过程中发生错误: {e}")
        error = ClassTableService.handle_service_error(e, "今日课程表查询")
        raise error


@router.get(
    "/classtable/week",
    response_model=WeekClassTableResponse,
    summary="获取指定日期所在周的课程表",
    description="获取指定日期所在周的课程表",
    tags=["课程表"],
)
async def get_week_classtable(
    query_date: str = Query(
        ..., description="查询日期，格式：YYYY-MM-DD", example="2025-01-01"
    ),
    session: requests.Session = Depends(get_user_session),
):
    """
    获取指定日期所在周的完整课程表

    - **query_date**: 查询日期，格式：YYYY-MM-DD

    返回该日期所在一周的完整课程表信息，包括：
    - 周数信息
    - 一周七天的课程安排
    - 每门课程的详细信息：课程名称、学分、属性、时间、地点、课堂名称
    """
    try:
        logger.info(f"收到周课程表查询请求，日期: {query_date}")

        # 验证日期格式
        try:
            datetime.strptime(query_date, "%Y-%m-%d")
        except ValueError:
            logger.warning(f"无效的日期格式: {query_date}")
            raise HTTPException(
                status_code=400, detail="日期格式无效，请使用 YYYY-MM-DD 格式"
            )

        # 调用服务获取周课程表
        week_courses = ClassTableService.get_week_courses(session, query_date)

        logger.info(
            f"周课程表查询成功，日期: {query_date}, 周数: {week_courses.week_number}"
        )
        return WeekClassTableResponse(
            success=True, message="周课程表获取成功", data=week_courses
        )

    except Exception as e:
        logger.error(f"周课程表查询过程中发生错误: {e}")
        error = ClassTableService.handle_service_error(e, "周课程表查询")
        raise error
