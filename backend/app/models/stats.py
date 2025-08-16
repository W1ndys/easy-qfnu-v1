"""
统计分析相关数据模型
定义课程统计、班内排名等相关的Pydantic模型
"""

from pydantic import BaseModel
from typing import List, Optional


class HistoricalStats(BaseModel):
    """历史统计数据模型"""

    course_id: str
    course_name: str
    semester: str
    average_score: float
    sample_count: int
    data_source: str = "historical"


class CrowdsourcedStats(BaseModel):
    """众包统计数据模型"""

    course_id: str
    course_name: str
    average_score: float
    sample_count: int
    data_source: str = "crowdsourced"
    last_updated: str


class CourseStatsResponse(BaseModel):
    """课程统计响应模型"""

    course_id: str
    course_name: str
    historical: Optional[HistoricalStats] = None
    crowdsourced: Optional[CrowdsourcedStats] = None
    combined_average: Optional[float] = None
    total_samples: int


class GradeContribution(BaseModel):
    """成绩贡献模型"""

    course_id: str
    course_name: str
    score: float
    class_id: Optional[str] = None
    semester: str


class ContributionRequest(BaseModel):
    """成绩贡献请求模型"""

    grades: List[GradeContribution]


class ClassRankResponse(BaseModel):
    """班内排名响应模型"""

    course_id: str
    course_name: str
    user_score: float
    rank: str  # 如 "5 / 35"
    percentile: float  # 百分位，如 0.85
    total_students: int
    class_average: float
    is_above_average: bool


class TeacherRecommendation(BaseModel):
    """教师推荐模型"""

    teacher_name: str
    course_name: str
    recommendation_score: float  # 推荐分数 (1-5)
    student_count: int  # 评价学生数量
    comments: List[str]  # 匿名评价
