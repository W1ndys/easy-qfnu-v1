from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Depends
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Float, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from app.core.security import get_current_user
from loguru import logger
import os

router = APIRouter()
Base = declarative_base()


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


class AverageScore(Base):
    __tablename__ = "average_scores"

    id = Column(Integer, primary_key=True)
    semester = Column(String, nullable=False)
    course_code = Column(String, nullable=False)
    course_name = Column(String, nullable=False)
    teacher = Column(String, nullable=False)
    average_score = Column(Float, nullable=False)
    student_count = Column(Integer, nullable=False)
    update_time = Column(String)


def get_db_engine():
    """获取数据库引擎"""
    logger.debug("开始获取数据库引擎...")

    # 使用 Path 对象进行路径操作，确保跨平台兼容性
    current_dir = Path(__file__).resolve().parent.parent.parent.parent
    db_path = current_dir / "data" / "average_scores.db"

    logger.debug(f"数据库路径: {db_path}")

    if not db_path.exists():
        logger.error(f"数据库文件不存在: {db_path}")
        raise HTTPException(status_code=404, detail="数据库文件不存在")

    # 使用 as_posix() 或直接使用 Path 对象都可以
    engine = create_engine(f"sqlite:///{db_path.as_posix()}")
    logger.debug("数据库引擎创建成功")
    return engine


def get_db_session():
    """获取数据库会话"""
    logger.debug("开始获取数据库会话...")
    try:
        engine = get_db_engine()
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        logger.debug("数据库会话创建成功")
        return session
    except Exception as e:
        logger.error(f"创建数据库会话失败: {e}")
        raise


def get_average_scores(
    course_identifier: str, teacher: Optional[str] = None
) -> Dict[str, Any]:
    """查询平均分数据"""
    logger.info(
        f"开始查询平均分数据，课程标识: {course_identifier}, 教师: {teacher or '全部'}"
    )

    try:
        session = get_db_session()
        logger.debug("数据库会话获取成功，开始构建查询...")

        # 构建基础查询
        query = session.query(AverageScore)

        # 构建课程查询条件（课程名称或课程代码）
        course_conditions = AverageScore.course_name.like(
            f"%{course_identifier}%"
        ) | AverageScore.course_code.like(f"%{course_identifier}%")

        # 应用课程查询条件
        query = query.filter(course_conditions)
        logger.debug(f"应用课程查询条件: {course_identifier}")

        # 如果指定了教师，添加教师查询条件
        if teacher and teacher.strip():
            teacher_condition = AverageScore.teacher.like(f"%{teacher.strip()}%")
            query = query.filter(teacher_condition)
            logger.debug(f"应用教师查询条件: {teacher.strip()}")

        # 使用text()函数进行智能排序，让最新的学期越靠前
        # 学期格式：年份-年份-数字，如"2023-2024-1"
        logger.debug("应用智能排序规则...")
        query = query.order_by(
            AverageScore.teacher,
            text("CAST(SUBSTR(semester, 1, 4) AS INTEGER) DESC"),  # 第一个年份降序
            text("CAST(SUBSTR(semester, 6, 4) AS INTEGER) DESC"),  # 第二个年份降序
            text("CAST(SUBSTR(semester, 11) AS INTEGER) DESC"),  # 学期数字降序
        )

        logger.debug("执行数据库查询...")
        results = query.all()
        logger.info(f"查询完成，返回 {len(results)} 条记录")

        session.close()
        logger.debug("数据库会话已关闭")

        if not results:
            # 提供更详细的错误信息
            if teacher and teacher.strip():
                error_msg = f"未找到课程名称或代码包含'{course_identifier}'且教师姓名包含'{teacher.strip()}'的数据"
                logger.warning(error_msg)
                raise HTTPException(status_code=404, detail=error_msg)
            else:
                error_msg = f"未找到课程名称或代码包含'{course_identifier}'的数据"
                logger.warning(error_msg)
                raise HTTPException(status_code=404, detail=error_msg)

        # 构建层级结构：课程->老师->学期->基准人数和平均分
        logger.debug("开始构建数据结构...")
        structured_data = {}

        for record in results:
            course_name = record.course_name
            teacher_name = record.teacher
            semester = record.semester

            # 初始化课程层级
            if course_name not in structured_data:
                structured_data[course_name] = {}

            # 初始化老师层级
            if teacher_name not in structured_data[course_name]:
                structured_data[course_name][teacher_name] = {}

            # 添加学期数据
            structured_data[course_name][teacher_name][semester] = {
                "average_score": record.average_score,
                "student_count": record.student_count,
                "update_time": record.update_time,
            }

        logger.info(f"数据结构构建完成，包含 {len(structured_data)} 个课程")
        return structured_data

    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        logger.error(f"数据库查询过程中发生错误: {e}")
        raise HTTPException(status_code=500, detail=f"数据库查询错误: {str(e)}")


@router.get(
    "/average-scores", summary="查询平均分", response_model=AverageScoreResponse
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
        data = get_average_scores(course, teacher)

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

    except HTTPException as e:
        logger.warning(f"平均分查询失败，HTTP状态码: {e.status_code}, 详情: {e.detail}")
        return AverageScoreResponse(code=e.status_code, message=e.detail, data={})
    except Exception as e:
        logger.error(f"平均分查询过程中发生未知错误: {e}")
        return AverageScoreResponse(code=500, message=f"未知错误: {str(e)}", data={})
