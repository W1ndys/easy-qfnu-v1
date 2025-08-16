"""
课表查询API端点
获取个人课程表信息
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
import logging

from app.core.database import get_db
from app.core.security import SessionExpiredError
from app.services.schedule_service import ScheduleService
from app.models.schedule import Schedule, CourseInfo

logger = logging.getLogger(__name__)

router = APIRouter()


class ScheduleResponse(BaseModel):
    """课表响应模型"""

    schedule: List[Schedule]
    current_week: int
    semester: str


@router.get("/schedule", response_model=ScheduleResponse, summary="获取个人课表")
async def get_schedule(
    week: Optional[int] = Query(None, description="周次，不传则获取当前周"),
    semester: Optional[str] = Query(None, description="学期，不传则获取当前学期"),
    current_user: dict = Depends(
        lambda: {"student_id": "test"}
    ),  # TODO: 实现真实的用户依赖
    db=Depends(get_db),
):
    """
    获取个人课程表

    Args:
        week: 可选的周次参数
        semester: 可选的学期参数
        current_user: 当前登录用户信息
        db: 数据库连接

    Returns:
        包含课表信息的响应
    """
    try:
        schedule_service = ScheduleService(db)

        # 获取课表数据
        schedule_data = await schedule_service.get_student_schedule(
            current_user["student_id"], week, semester
        )

        logger.info(f"成功获取用户 {current_user['student_id']} 的课表数据")

        return schedule_data

    except SessionExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="学校官网Session已过期，请重新登录",
            headers={"X-Session-Expired": "true"},
        )
    except Exception as e:
        logger.error(f"获取课表过程发生错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取课表失败，请稍后重试",
        )


@router.get("/schedule/today", summary="获取今日课程")
async def get_today_schedule(
    current_user: dict = Depends(
        lambda: {"student_id": "test"}
    ),  # TODO: 实现真实的用户依赖
    db=Depends(get_db),
):
    """
    获取今日课程安排
    """
    try:
        schedule_service = ScheduleService(db)

        # 获取今日课程
        today_courses = await schedule_service.get_today_courses(
            current_user["student_id"]
        )

        return {"courses": today_courses, "date": schedule_service.get_current_date()}

    except SessionExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="学校官网Session已过期，请重新登录",
            headers={"X-Session-Expired": "true"},
        )
    except Exception as e:
        logger.error(f"获取今日课程过程发生错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="获取今日课程失败"
        )


@router.get("/courses/{course_id}/capacity", summary="查询课余量")
async def get_course_capacity(
    course_id: str,
    current_user: dict = Depends(
        lambda: {"student_id": "test"}
    ),  # TODO: 实现真实的用户依赖
    db=Depends(get_db),
):
    """
    查询指定课程的剩余可选名额

    Args:
        course_id: 课程ID
        current_user: 当前登录用户信息
        db: 数据库连接

    Returns:
        课程容量信息
    """
    try:
        schedule_service = ScheduleService(db)

        # 获取课程容量信息
        capacity_info = await schedule_service.get_course_capacity(
            current_user["student_id"], course_id
        )

        return capacity_info

    except SessionExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="学校官网Session已过期，请重新登录",
            headers={"X-Session-Expired": "true"},
        )
    except Exception as e:
        logger.error(f"获取课程容量过程发生错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="获取课程容量失败"
        )
