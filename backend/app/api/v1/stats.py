"""
数据统计API端点
处理课程成绩分析、班内排名等统计功能
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
import logging

from app.core.database import get_db
from app.core.config import settings
from app.services.stats_service import StatsService
from app.models.stats import CourseStatsResponse, ClassRankResponse, ContributionRequest

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/stats/course/", response_model=CourseStatsResponse, summary="查询课程综合成绩分析"
)
async def get_course_stats(
    course_id: str = Query(..., description="课程ID"),
    current_user: dict = Depends(
        lambda: {"student_id": "test"}
    ),  # TODO: 实现真实的用户依赖
    db=Depends(get_db),
):
    """
    获取课程综合成绩分析

    结合历史参考数据和用户众包数据，提供课程历史平均分等统计信息

    Args:
        course_id: 课程ID
        current_user: 当前登录用户信息
        db: 数据库连接

    Returns:
        课程统计分析结果
    """
    try:
        stats_service = StatsService(db)

        # 获取课程统计数据
        course_stats = await stats_service.get_course_statistics(course_id)

        logger.info(f"成功获取课程 {course_id} 的统计数据")

        return course_stats

    except Exception as e:
        logger.error(f"获取课程统计数据过程发生错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取课程统计数据失败",
        )


@router.post("/stats/grades/contribute", summary="用户贡献个人成绩")
async def contribute_grades(
    contribution_data: ContributionRequest,
    current_user: dict = Depends(
        lambda: {"student_id": "test"}
    ),  # TODO: 实现真实的用户依赖
    db=Depends(get_db),
):
    """
    用户贡献个人成绩数据

    用户可以选择将自己的成绩数据匿名贡献给系统，
    用于改善课程统计和班内排名功能

    Args:
        contribution_data: 贡献的成绩数据
        current_user: 当前登录用户信息
        db: 数据库连接

    Returns:
        贡献结果
    """
    try:
        stats_service = StatsService(db)

        # 检查用户是否同意数据贡献
        user_preference = await stats_service.check_contribution_preference(
            current_user["student_id"]
        )

        if not user_preference:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="用户未同意数据贡献"
            )

        # 处理成绩贡献
        result = await stats_service.contribute_grades(
            current_user["student_id"], contribution_data.grades
        )

        logger.info(
            f"用户 {current_user['student_id']} 成功贡献了 {len(contribution_data.grades)} 条成绩数据"
        )

        return result

    except Exception as e:
        logger.error(f"贡献成绩数据过程发生错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="贡献成绩数据失败"
        )


@router.get(
    "/stats/class_rank/",
    response_model=ClassRankResponse,
    summary="获取个人在班内的成绩分析",
)
async def get_class_rank(
    course_id: str = Query(..., description="课程ID"),
    current_user: dict = Depends(
        lambda: {"student_id": "test"}
    ),  # TODO: 实现真实的用户依赖
    db=Depends(get_db),
):
    """
    获取个人在班内的成绩分析

    基于用户授权的众包数据，为用户单独、私密地展示
    其单科成绩在班内的百分位和精确排名

    Args:
        course_id: 课程ID
        current_user: 当前登录用户信息
        db: 数据库连接

    Returns:
        班内排名分析结果
    """
    try:
        stats_service = StatsService(db)

        # 获取班内排名数据
        rank_data = await stats_service.get_class_rank(
            current_user["student_id"], course_id
        )

        # 检查数据量是否足够
        if rank_data.total_students < settings.MIN_DATA_FOR_RANKING:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"班内数据量不足，需要至少 {settings.MIN_DATA_FOR_RANKING} 位同学的数据",
            )

        logger.info(
            f"成功获取用户 {current_user['student_id']} 在课程 {course_id} 的班内排名"
        )

        return rank_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取班内排名过程发生错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="获取班内排名失败"
        )


@router.post("/stats/contribution/preference", summary="设置数据贡献偏好")
async def set_contribution_preference(
    enabled: bool,
    current_user: dict = Depends(
        lambda: {"student_id": "test"}
    ),  # TODO: 实现真实的用户依赖
    db=Depends(get_db),
):
    """
    设置用户的数据贡献偏好

    Args:
        enabled: 是否同意贡献数据
        current_user: 当前登录用户信息
        db: 数据库连接

    Returns:
        设置结果
    """
    try:
        stats_service = StatsService(db)

        # 更新用户贡献偏好
        await stats_service.update_contribution_preference(
            current_user["student_id"], enabled
        )

        logger.info(
            f"用户 {current_user['student_id']} 数据贡献偏好已更新为: {enabled}"
        )

        return {"success": True, "preference": enabled, "message": "偏好设置已更新"}

    except Exception as e:
        logger.error(f"设置贡献偏好过程发生错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="设置偏好失败"
        )
