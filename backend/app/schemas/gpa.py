# app/schemas/gpa.py (重构后)
from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class GPACalculateRequest(BaseModel):
    include_indices: List[int] = []  # 要排除的课程序号列表
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
    """GPA分析结果（/grades 不返回 courses，/gpa/calculate 可能返回）"""

    weighted_gpa: float
    total_credit: float
    course_count: int
    courses: Optional[List[Dict[str, Any]]] = None


# --- ↓↓↓ 核心修改部分：更新此模型以匹配新的API结构 ↓↓↓ ---
class GradesResponse(BaseModel):
    """(新版) 成绩查询响应模型"""

    success: bool
    message: str
    data: List[CourseGrade]
    basic_gpa: Optional[GPAAnalysis] = None
    effective_gpa: Optional[GPAAnalysis] = None
    semester_gpa: Optional[Dict[str, GPAAnalysis]] = None
    yearly_gpa: Optional[Dict[str, GPAAnalysis]] = None


# --- ↑↑↑ 核心修改部分 ↑↑↑ ---


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
