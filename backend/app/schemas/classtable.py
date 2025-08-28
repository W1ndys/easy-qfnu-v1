# app/schemas/classtable.py
from pydantic import BaseModel
from typing import List, Dict, Any


class WeekInfo(BaseModel):
    """周信息"""

    current_week: int
    total_weeks: int


class TimeSlot(BaseModel):
    """时间段信息"""

    period: int
    name: str
    time: str
    slots: List[int]


class Weekday(BaseModel):
    """星期信息"""

    id: int
    name: str
    short: str


class CourseTimeInfo(BaseModel):
    """课程时间信息"""

    weekday: int
    weekday_name: str
    period: int
    period_name: str
    time_slots: List[int]
    actual_periods: List[int]  # 新增：实际节次信息
    start_time: str
    end_time: str
    is_cross_period: bool  # 新增：是否跨大节课程


class CourseStyle(BaseModel):
    """课程样式信息"""

    row: int
    col: int
    row_span: int
    col_span: int


class CourseRawData(BaseModel):
    """课程原始数据"""

    course_name: str
    credits: str
    course_type: str
    time_detail: str
    location: str
    class_name: str
    weeks: List[int]
    actual_periods: List[int] = []  # 新增：解析出的具体节次


class Course(BaseModel):
    """课程信息"""

    id: str
    name: str
    location: str
    classroom: str
    credits: str
    course_type: str
    class_name: str
    weeks: List[int]
    time_info: CourseTimeInfo
    style: CourseStyle
    raw_data: CourseRawData


class CourseStats(BaseModel):
    """课程统计信息"""

    total_courses: int
    total_hours: int
    courses_by_day: Dict[str, int]


class ClassTableData(BaseModel):
    """课程表数据"""

    week_info: WeekInfo
    time_slots: List[TimeSlot]
    weekdays: List[Weekday]
    courses: List[Course]
    stats: CourseStats


class ClassTableResponse(BaseModel):
    """课程表响应"""

    success: bool
    message: str
    data: ClassTableData


class ClassTableInfoData(BaseModel):
    """课程表基础信息数据"""

    time_slots: List[TimeSlot]
    weekdays: List[Weekday]


class ClassTableInfoResponse(BaseModel):
    """课程表基础信息响应"""

    success: bool
    message: str
    data: ClassTableInfoData


class ErrorResponse(BaseModel):
    """错误响应"""

    success: bool = False
    message: str
    data: Dict[str, Any] = {}
