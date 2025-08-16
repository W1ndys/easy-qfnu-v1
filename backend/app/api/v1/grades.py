"""
成绩查询API端点
获取个人成绩信息和统计数据
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
import logging

from app.core.database import get_db
from app.core.security import SessionExpiredError
from app.services.grade_service import GradeService
from app.models.grade import Grade, GradeStats

logger = logging.getLogger(__name__)

router = APIRouter()


class GradeResponse(BaseModel):
    """成绩响应模型"""

    grades: List[Grade]
    stats: GradeStats


@router.get("/grades", response_model=GradeResponse, summary="获取个人成绩")
async def get_grades(
    semester: Optional[str] = Query(
        None, description="学期，如'2023-2024-1'，不传则获取所有学期"
    ),
    current_user: dict = Depends(
        lambda: {"student_id": "test"}
    ),  # TODO: 实现真实的用户依赖
    db=Depends(get_db),
):
    """
    获取个人成绩信息

    Args:
        semester: 可选的学期参数，不传则获取所有成绩
        current_user: 当前登录用户信息
        db: 数据库连接

    Returns:
        包含成绩列表和统计信息的响应
    """
    try:
        grade_service = GradeService(db)

        # 获取成绩数据
        grades = await grade_service.get_student_grades(
            current_user["student_id"], semester
        )

        # 计算统计信息
        stats = await grade_service.calculate_grade_stats(grades)

        logger.info(f"成功获取用户 {current_user['student_id']} 的成绩数据")

        return GradeResponse(grades=grades, stats=stats)

    except SessionExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="学校官网Session已过期，请重新登录",
            headers={"X-Session-Expired": "true"},
        )
    except Exception as e:
        logger.error(f"获取成绩过程发生错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取成绩失败，请稍后重试",
        )


@router.get("/grades/summary", summary="获取成绩摘要")
async def get_grade_summary(
    current_user: dict = Depends(
        lambda: {"student_id": "test"}
    ),  # TODO: 实现真实的用户依赖
    db=Depends(get_db),
):
    """
    获取成绩摘要信息
    包括总GPA、学分统计等关键指标
    """
    try:
        grade_service = GradeService(db)

        # 获取所有成绩
        grades = await grade_service.get_student_grades(current_user["student_id"])

        # 计算摘要统计
        summary = await grade_service.calculate_summary_stats(grades)

        return summary

    except SessionExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="学校官网Session已过期，请重新登录",
            headers={"X-Session-Expired": "true"},
        )
    except Exception as e:
        logger.error(f"获取成绩摘要过程发生错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="获取成绩摘要失败"
        )
