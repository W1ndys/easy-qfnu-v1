"""
成绩相关数据模型
定义成绩查询和统计相关的Pydantic模型
"""

from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal


class Grade(BaseModel):
    """单科成绩模型"""

    course_id: str
    course_name: str
    semester: str
    score: float
    credit: float
    grade_point: Optional[float] = None
    course_type: Optional[str] = None  # 必修、选修等
    teacher: Optional[str] = None
    exam_type: Optional[str] = None  # 期末、补考等


class GradeStats(BaseModel):
    """成绩统计模型"""

    total_courses: int
    total_credits: float
    gpa: float  # 总GPA
    weighted_average: float  # 加权平均分
    failed_courses: int  # 挂科门数
    excellent_courses: int  # 90分以上门数


class SemesterGrades(BaseModel):
    """学期成绩模型"""

    semester: str
    grades: List[Grade]
    semester_gpa: float
    semester_average: float
    semester_credits: float


class GradeSummary(BaseModel):
    """成绩摘要模型"""

    overall_stats: GradeStats
    semester_stats: List[SemesterGrades]
    trend_analysis: Optional[dict] = None  # 成绩趋势分析
