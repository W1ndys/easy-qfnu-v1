from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Float, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
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
    # 使用 Path 对象进行路径操作，确保跨平台兼容性
    current_dir = Path(__file__).resolve().parent.parent.parent.parent
    db_path = current_dir / "data" / "average_scores.db"

    if not db_path.exists():
        raise HTTPException(status_code=404, detail="数据库文件不存在")

    # 使用 as_posix() 或直接使用 Path 对象都可以
    engine = create_engine(f"sqlite:///{db_path.as_posix()}")
    return engine


def get_db_session():
    """获取数据库会话"""
    engine = get_db_engine()
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


def get_average_scores(
    course_identifier: str, teacher: Optional[str] = None
) -> Dict[str, Any]:
    """查询平均分数据"""
    try:
        session = get_db_session()

        # 构建查询 - 支持按课程名称或课程代码查询
        query = session.query(AverageScore).filter(
            (AverageScore.course_name == course_identifier)
            | (AverageScore.course_code == course_identifier)
        )

        if teacher:
            query = query.filter(AverageScore.teacher == teacher)

        query = query.order_by(AverageScore.teacher, AverageScore.semester)
        results = query.all()

        session.close()

        if not results:
            return {}

        # 构建层级结构：课程->老师->学期->基准人数和平均分
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

        return structured_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库查询错误: {str(e)}")


@router.get(
    "/average-scores", summary="查询平均分", response_model=AverageScoreResponse
)
async def query_average_scores(
    course: str = Query(..., description="课程名称或课程代码（必填）", min_length=1),
    teacher: Optional[str] = Query(
        None, description="教师姓名（选填，为空则查询所有老师）", min_length=1
    ),
) -> AverageScoreResponse:
    """
    查询指定课程的平均分数据

    - **course**: 课程名称或课程代码（必填）
    - **teacher**: 教师姓名（选填，不填则查询该课程所有老师的数据）

    返回格式：课程->老师->学期->基准人数和平均分
    """
    try:
        data = get_average_scores(course, teacher)

        if not data:
            return AverageScoreResponse(code=404, message="未找到相关数据", data={})

        # 转换数据格式以符合响应模型
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

        return AverageScoreResponse(code=200, message="查询成功", data=formatted_data)

    except HTTPException as e:
        return AverageScoreResponse(code=e.status_code, message=e.detail, data={})
    except Exception as e:
        return AverageScoreResponse(code=500, message=f"未知错误: {str(e)}", data={})
