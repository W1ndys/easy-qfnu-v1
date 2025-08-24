# app/schemas/profile.py
from pydantic import BaseModel
from typing import Optional


class StudentProfile(BaseModel):
    """学生个人信息模型"""

    student_name: str  # 学生姓名
    student_id: str  # 学生编号
    college: str  # 所属院系
    major: str  # 专业名称
    class_name: str  # 班级名称


class ProfileResponse(BaseModel):
    """个人信息响应模型"""

    success: bool
    message: str
    data: Optional[StudentProfile] = None
