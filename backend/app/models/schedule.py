"""
课表相关数据模型
定义课程表查询相关的Pydantic模型
"""

from pydantic import BaseModel
from typing import List, Optional


class CourseInfo(BaseModel):
    """课程信息模型"""

    course_id: str
    course_name: str
    teacher: str
    location: str
    capacity: Optional[int] = None  # 课程容量
    enrolled: Optional[int] = None  # 已选人数


class Schedule(BaseModel):
    """课表条目模型"""

    course_info: CourseInfo
    week_day: int  # 星期几 (1-7)
    start_time: str  # 开始时间，如"08:00"
    end_time: str  # 结束时间，如"09:40"
    weeks: str  # 上课周次，如"1-16周"
    class_period: str  # 节次，如"1-2节"


class DaySchedule(BaseModel):
    """单日课表模型"""

    date: str  # 日期
    week_day: int  # 星期几
    courses: List[Schedule]


class WeekSchedule(BaseModel):
    """周课表模型"""

    week_number: int
    semester: str
    days: List[DaySchedule]


class CourseCapacity(BaseModel):
    """课程容量信息模型"""

    course_id: str
    course_name: str
    total_capacity: int
    enrolled_count: int
    available_spots: int
    is_full: bool


class ScheduleResponse(BaseModel):
    """课表响应模型"""

    schedule: List[Schedule]
    current_week: int
    semester: str
