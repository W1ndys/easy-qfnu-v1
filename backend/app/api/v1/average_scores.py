from typing import Optional, Dict, Any
from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel
from app.core.security import get_current_user
from app.services.average_scores import average_scores_service
from loguru import logger


router = APIRouter()


# Pydantic 响应模型
class SemesterData(BaseModel):
    """学期数据模型"""

    average_score: float
    student_count: int
    update_time: Optional[str] = None


class AverageScoreResponse(BaseModel):
    """平均分查询响应模型"""

    code: int
    message: str
    data: Dict[str, Dict[str, Dict[str, SemesterData]]]  # 课程 -> 教师 -> 学期 -> 数据


@router.get(
    "/average-scores",
    summary="查询平均分",
    response_model=AverageScoreResponse,
    tags=["成绩"],
)
async def query_average_scores(
    course: str = Query(
        ...,
        description="课程名称或课程代码（必填，支持模糊查询，至少3个字符）",
        min_length=3,
    ),
    teacher: Optional[str] = Query(
        None,
        description="教师姓名（选填，支持模糊查询，至少2个字符，为空则查询所有老师）",
        min_length=2,
    ),
    current_user: str = Depends(get_current_user),
) -> AverageScoreResponse:
    """
    查询指定课程的平均分数据

    - **course**: 课程名称或课程代码（必填，支持模糊查询，至少3个字符）
    - **teacher**: 教师姓名（选填，支持模糊查询，至少2个字符，不填则查询该课程所有老师的数据）

    **权限要求：** 需要有效的JWT Token认证
    **模糊查询：** 所有查询参数都支持模糊匹配
    **长度限制：** 课程名称至少需要3个字符，教师姓名至少需要2个字符，提高查询成功率

    返回格式：课程->老师->学期->基准人数和平均分
    """
    logger.info(
        f"收到平均分查询请求，用户: {current_user}, 课程: {course}, 教师: {teacher or '全部'}"
    )

    try:
        logger.debug("开始查询平均分数据...")
        data = average_scores_service.query_average_scores(course, teacher)

        if not data:
            logger.warning("查询结果为空")
            return AverageScoreResponse(code=404, message="未找到相关数据", data={})

        # 转换数据格式以符合响应模型
        logger.debug("开始转换数据格式...")
        formatted_data = {}
        for course_name, teachers in data.items():
            formatted_data[course_name] = {}
            for teacher_name, semesters in teachers.items():
                formatted_data[course_name][teacher_name] = {}
                for semester, sem_data in semesters.items():
                    formatted_data[course_name][teacher_name][semester] = SemesterData(
                        average_score=sem_data["average_score"],
                        student_count=sem_data["student_count"],
                        update_time=sem_data["update_time"],
                    )

        logger.info(f"平均分查询成功，返回 {len(formatted_data)} 个课程的数据")
        return AverageScoreResponse(code=200, message="查询成功", data=formatted_data)

    except ValueError as ve:
        # 处理数据未找到的情况
        logger.warning(f"平均分查询失败: {ve}")
        return AverageScoreResponse(code=404, message=str(ve), data={})
    except Exception as e:
        logger.error(f"平均分查询过程中发生未知错误: {e}")
        return AverageScoreResponse(code=500, message=f"未知错误: {str(e)}", data={})
