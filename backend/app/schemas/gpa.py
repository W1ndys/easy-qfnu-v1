# app/schemas/gpa.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class GPACalculateRequest(BaseModel):
    exclude_indices: List[int] = []  # 要排除的课程序号列表
    remove_retakes: bool = False  # 是否去除重修补考，取最高绩点


class CourseGrade(BaseModel):
    """单个课程成绩信息"""

    index: str
    semester: str
    courseCode: str
    courseName: str
    groupName: str
    score: str
    scoreTag: str
    credit: str
    totalHours: str
    gpa: str
    retakeSemester: str
    assessmentMethod: str
    examType: str
    courseAttribute: str
    courseNature: str
    courseCategory: str


class GPAAnalysis(BaseModel):
    """GPA分析结果"""

    weighted_gpa: float
    total_credit: float
    course_count: int
    courses: List[Dict[str, Any]]


class GradesResponse(BaseModel):
    """成绩查询响应模型"""

    success: bool
    message: str
    data: List[CourseGrade]
    gpa_analysis: Optional[Dict[str, GPAAnalysis]] = None
    total_courses: Optional[int] = None


class GPACalculateResponse(BaseModel):
    """GPA计算响应模型"""

    success: bool
    message: str
    data: GPAAnalysis


class SemesterResponse(BaseModel):
    """学期列表响应模型"""

    success: bool
    message: str
    data: List[str]


class ErrorResponse(BaseModel):
    """错误响应模型"""

    detail: str
